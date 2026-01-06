import uuid
import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from myfinances.tests.factories import (
    UserFactory, GroupFactory, CategoryFactory
)
from myfinances.models import CategoryList


@pytest.mark.django_db
def test_category_detail_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    cat1 = CategoryFactory(user_group=group1)
    cat2 = CategoryFactory(user_group=group2)

    client.force_login(user)

    # Allowed
    url = reverse("myfinances:category-detail", args=[cat1.pk])
    response = client.get(url)
    assert response.status_code == 200

    # Denied (404)
    url = reverse("myfinances:category-detail", args=[cat2.pk])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_create_assigns_group_and_owner(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    client.force_login(user)

    url = reverse("myfinances:category-new")

    name = f"Food-{uuid.uuid4()}"
    response = client.post(url, {"name": name, "label": "Expense"})

    assert response.status_code == 302  # redirect on success

    cat = CategoryList.objects.latest("id")
    assert cat.user_group == group
    assert cat.owner == user


@pytest.mark.django_db
def test_category_update_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    cat1 = CategoryFactory(user_group=group1)
    cat2 = CategoryFactory(user_group=group2)

    client.force_login(user)

    url = reverse("myfinances:category-update", args=[cat1.pk])
    response = client.post(url, {"name": "Updated", "label": "Expense"})

    assert response.status_code == 302

    cat1.refresh_from_db()
    assert cat1.name == "Updated"
    assert cat1.label == "Expense"


@pytest.mark.django_db
def test_category_delete_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    cat1 = CategoryFactory(user_group=group1)
    cat2 = CategoryFactory(user_group=group2)

    client.force_login(user)

    # Allowed
    url = reverse("myfinances:category-delete", args=[cat1.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert not CategoryList.objects.filter(pk=cat1.pk).exists()

    # Denied
    url = reverse("myfinances:category-delete", args=[cat2.pk])
    response = client.post(url)
    assert response.status_code == 404
