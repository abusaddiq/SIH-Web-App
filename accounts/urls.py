from django.urls import path

from .views import (
    login_view,
    logout_view,
    password_change_view,
    my_account,
    user_list,
    user_create,
    user_edit,
    user_toggle,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("password/change/", password_change_view, name="password_change"),
    path("my-account/", my_account, name="my_account"),
    path("admin/users/", user_list, name="accounts-user-list"),
    path("admin/users/new/", user_create, name="accounts-user-create"),
    path("admin/users/<int:pk>/", user_edit, name="accounts-user-edit"),
    path("admin/users/<int:pk>/toggle/", user_toggle, name="accounts-user-toggle"),
]