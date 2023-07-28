
"""
Questions:


    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other.
    Consider the following: if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this


    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_activity()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

import re
import unittest
import uuid


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


payment_feed: [Payment] = []


class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.friends: [User] = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')

    def retrieve_feed(self) -> [Payment]:
        return list(filter(lambda x: x.actor == self, payment_feed))

    def add_friend(self, new_friend):
        self.friends.append(new_friend)
        new_friend.friends.append(self)

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):

        if amount <= self.balance:
            return self.pay_with_balance(target, amount, note)

        return self.pay_with_card(target, amount, note)

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        self._common_validations(target, amount)

        if self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)
        payment_feed.append(payment)
        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        self._common_validations(target, amount)
        self._pay_with_balance(amount)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)
        payment_feed.append(payment)
        return payment

    def _common_validations(self, target, amount):
        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass

    def _pay_with_balance(self, amount):
        self.balance -= amount


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        user = User(username)
        user.add_to_balance(balance)
        user.add_credit_card(credit_card_number)
        return user

    def render_feed(self, feed: [Payment] = None):
        if feed:
            for payment in feed:
                if feed.actor in feed.target.friends or feed.target in feed.actor.friends:
                    print(f"{feed.actor} paid to his friend {payment.target} ${payment.amount:.2f} for {payment.note}.")
                else:
                    print(f"{feed.actor} paid {payment.target} ${payment.amount:.2f} for {payment.note}")
        else:
            print("No feed found.")

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):
    def setUp(self):
        self.venmo = MiniVenmo()

    def test_create_user(self):
        name = "Andres"
        balance = 10.0
        credit_card = "4111111111111111"

        user = self.venmo.create_user(name, balance, credit_card)

        assert user.username == "Andres"
        assert user.balance == 10.0

    def test_create_user_with_negative_amount(self):

        name = "Andres"
        balance = -10.0
        credit_card = "4111111111111111"

        with self.assertRaises(PaymentException):
            self.venmo.create_user(name, balance, credit_card)

    def test_add_balance_to_user(self):
        name = "Andres"
        balance = 0.00
        credit_card = "4111111111111111"

        user = self.venmo.create_user(name, balance, credit_card)

        assert user.username == "Andres"
        assert user.balance == 0.0
        user.add_to_balance(15.0)
        assert user.balance == 15.0

    def test_payment(self):
        name = "Andres"
        balance = 25.00
        credit_card = "4111111111111111"
        user = self.venmo.create_user(name, balance, credit_card)

        name_2 = "Ivan"
        balance_2 = 0.00
        credit_card_2 = "4111111111111111"
        user_2 = self.venmo.create_user(name_2, balance_2, credit_card_2)

        user.pay(user_2, 15.00, "Coffee")

        assert user.username == "Andres"
        assert user.balance == 10.0

        assert user_2.username == "Ivan"
        assert user_2.balance == 15.0

    def test_payment_to_the_same_user(self):
        name = "Andres"
        balance = 25.00
        credit_card = "4111111111111111"
        user = self.venmo.create_user(name, balance, credit_card)

        with self.assertRaises(PaymentException):
            user.pay(user, 15.00, "Coffee")


if __name__ == '__main__':
    unittest.main()

