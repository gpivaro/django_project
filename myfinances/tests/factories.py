import decimal
import datetime
import factory
from django.contrib.auth.models import User, Group
from myfinances.models import CategoryList, Statements, Item


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"group-{n}")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user-{n}")

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoryList

    name = factory.Sequence(lambda n: f"Category-{n}")
    label = "Expense"
    owner = factory.SubFactory(UserFactory)
    user_group = factory.SubFactory(GroupFactory)


class StatementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Statements

    Details = factory.Sequence(lambda n: f"Details-{n}")
    Posting_Date = factory.LazyFunction(lambda: datetime.date.today())
    Description = factory.Sequence(lambda n: f"Description-{n}")
    Amount = factory.LazyFunction(lambda: float(10.00))
    Type = "debit"
    Balance = factory.LazyFunction(lambda: float(100.00))
    Check_Slip = ""
    Owner = factory.SubFactory(UserFactory)
    user_group = factory.SubFactory(GroupFactory)
    Acct_Info = "1234"


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    Description = factory.Sequence(lambda n: f"Item-{n}")
    user_group = factory.SubFactory(GroupFactory)
