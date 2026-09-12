"""AI Assistance abstraction layer.

The provider is selected via the `AI_PROVIDER` environment variable.
- "rules": offline, rule-based answers built ONLY from published CMS data.
  It never invents prices, availability, confirmations, policies or capacity.
- Future providers (OpenAI, Anthropic, etc.) implement the same `AIProvider` interface.
"""
import re

from django.conf import settings

from facilities.models import Facility
from programmes.models import Programme


class AIProvider:
    name = "base"
    label = "Base provider"

    def answer(self, question: str) -> str:
        raise NotImplementedError

    def safe_intro(self) -> str:
        return (
            "I answer only from information published by SPAK Innovation Hub. "
            "For anything not covered, please contact SPAK or submit an enquiry via the Contact page."
        )


class RulesProvider(AIProvider):
    """Default offline provider that answers strictly from CMS data."""

    name = "rules"
    label = "SPAK Information Assistant (offline)"

    def _published_facilities(self):
        return Facility.objects.filter(status="published").prefetch_related("prices")

    def _published_programmes(self):
        return Programme.objects.filter(status="published")

    def answer(self, question: str) -> str:
        q = question.strip().lower()
        if not q:
            return "Please type a question about SPAK Innovation Hub."
        if any(w in q for w in ("hello", "hi ", "hey")):
            return (
                "Hello! I'm the SPAK Information Assistant.\n\nI can help with questions about "
                "facilities, services, programmes, training and booking steps — using only "
                "information SPAK has published. How can I help?"
            )
        if any(w in q for w in ("facilit", "cowork", "co-work", "office", "room", "hall")):
            return self._facilities_answer(q)
        if any(w in q for w in ("price", "cost", "fee", "charge", "how much", "rate")):
            return self._pricing_answer(q)
        if any(w in q for w in ("book", "reserve")):
            return self._booking_answer()
        if any(w in q for w in ("programme", "program ", "training", "workshop", "event", "bootcamp", "seminar")):
            return self._programmes_answer(q)
        if any(w in q for w in ("contact", "phone", "email", "address", "reach", "where", "located", "location", "open", "hour", "whatsapp")):
            return self._contact_answer()
        if any(w in q for w in ("about", "what is spak", "who is spak", "who are you")):
            return self._about_answer()
        return self._fallback(q)

    def _facilities_answer(self, q):
        facilities = self._published_facilities()
        if not facilities.exists():
            return "No facilities are currently listed. Please contact SPAK or submit an enquiry."
        lines = ["Based on the current published SPAK information, these facilities are available:"]
        for f in facilities:
            prices = " | ".join(
                f"{p.get_price_type_display()}: {p.amount} {p.currency}" for p in f.current_prices
            ) or "pricing to be confirmed"
            cap = f" {f.capacity} capacity" if f.capacity else ""
            lines.append(f"- **{f.name}** (capacity {f.capacity or 'n/a'}). {prices}.")
        lines.append("For availability or to book, visit the facility page and use Book Now, or contact SPAK.")
        return "\n".join(lines)

    def _pricing_answer(self, q):
        facilities = self._published_facilities()
        out = []
        for f in facilities:
            prices = list(f.current_prices)
            if not prices:
                continue
            out.append(f"- **{f.name}**: " + ", ".join(
                f"{p.get_price_type_display()} {p.amount} {p.currency}" for p in prices
            ))
        if not out:
            return "I'm sorry, but I don't have published pricing information yet. Please contact SPAK via the Contact page for official prices."
        return (
            "Here is the pricing currently published by SPAK (this may change — please confirm with SPAK before relying on it):\n\n"
            + "\n".join(out)
            + "\n\nPrices shown are as published on the website at this time."
        )

    def _booking_answer(self):
        return (
            "To book a facility:\n\n"
            "1. Go to the Facilities page and open the facility you need (e.g. Meeting Rooms).\n"
            "2. Select **Book Now** and complete the booking form.\n"
            "3. Submit the form. This creates a **booking request** — it is NOT a confirmation.\n"
            "4. SPAK will review the request and confirm availability.\n\n"
            "A booking becomes confirmed only after SPAK approves it."
        )

    def _programmes_answer(self, q):
        programmes = self._published_programmes()
        if not programmes.exists():
            return "No programmes are currently published. Please check back soon or contact SPAK."
        lines = ["Programmes currently published:"]
        for p in programmes.order_by("-start_date")[:10]:
            when = f"{p.start_date} - {p.end_date}" if p.end_date else str(p.start_date or "TBC")
            venue = p.venue or (p.get_programme_type_display() or "")
            lines.append(f"- **{p.title}** ({when}, {venue}). Audience: {p.target_audience or 'open'}. Registration: {p.registration_button_label}.")
        return "\n".join(lines)

    def _contact_answer(self):
        from core.models import ContactSettings

        cs = ContactSettings.get()
        parts = ["You can reach SPAK Innovation Hub here:"]
        if cs.address:
            parts.append(f"- Address: {cs.address}")
        if cs.phone_1:
            parts.append(f"- Phone: {cs.phone_1}")
        if cs.email_1:
            parts.append(f"- Email: {cs.email_1}")
        if cs.whatsapp:
            parts.append(f"- WhatsApp: {cs.whatsapp}")
        if cs.working_hours:
            parts.append(f"- Working hours: {cs.working_hours}")
        parts.append("Or use the contact form on the /contact page and SPAK will respond.")
        return "\n".join(parts)

    def _about_answer(self):
        from core.models import CmsPage

        page = CmsPage.objects.filter(slug="about", is_published=True).first()
        if page and page.summary:
            return f"{page.summary}\n\nVisit the About page for the full story."
        return "You can read about SPAK Innovation Hub on the About page. For anything else, please contact SPAK directly."

    def _fallback(self, q):
        return (
            "I don't have enough published information to answer that confidently.\n\n"
            "Please contact SPAK Innovation Hub directly or submit an enquiry via the Contact page, "
            "and a team member will assist you."
        )


def get_assistant(request=None) -> AIProvider:
    provider_name = settings.AI_PROVIDER
    if provider_name in ("openai", "anthropic", "gemini") and settings.AI_API_KEY:
        # Replace with a real provider when selected. Interface preserved for future swap.
        from .providers import CloudProvider

        return CloudProvider(provider_name, settings.AI_API_KEY, settings.AI_MODEL)
    return RulesProvider()