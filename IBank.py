# from generators import get_user_data
from abc import ABC, abstractmethod
from datetime import datetime


class AccountBase(ABC):
    def __init__(self, name, passport8, phone_number, start_balance=0):
        self.name = name
        self.passport8 = passport8
        self.phone_number = phone_number
        self.balance = start_balance

    @abstractmethod
    def transfer(self, target_account, amount):
        """
        Перевод денег на счет другого клиента
        :param target_account: счет клиента для перевода
        :param amount: сумма перевода
        :return:
        """
        pass

    @abstractmethod
    def deposit(self, amount):
        """
        Внесение суммы на текущий счет
        :param amount: сумма
        """
        pass

    @abstractmethod
    def withdraw(self, amount):
        """
        Снятие суммы с текущего счета
        :param amount: сумма
        """
        pass

    @abstractmethod
    def full_info(self):
        """
        Полная информация о счете в формате: "Иванов Иван Петрович баланс: 100 руб. паспорт: 12345678 т.89002000203"
        """
        return f"..."

    @abstractmethod
    def __repr__(self):
        """
        :return: Информацию о счете в виде строки в формате "Иванов И.П. баланс: 100 руб."
        """
        return f"..."


class Operation:
    TRANSFER = "transfer"
    WITHDRAW = "withdraw"
    DEPOSIT = "deposit"

    def __init__(self, type, amount, target=None, fee=0):
        self.date = datetime.now()
        self.type = type
        self.amount = amount
        self.target = target
        self.fee = fee  # fee summ

    def __repr__(self):
        target = self.target.name if self.target else ""
        return f"({self.date}) {self.type}: sum: {self.amount} {target}"


class Account(AccountBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []
        self.__fee = 2  # 2%
        # self.name = name
        self.passport8 = self._validate_passport(args[1])
        self.phone_number = self._validate_phone(args[2])
        self._archive = False


    def _validate_phone(self, phone):
        import re
        pattern = re.compile(r'\+7\d{3}-\d{3}-\d{2}-\d{2}')
        if re.search(pattern, phone):
            return phone
        raise ValueError('Номер телефона указан в неверном формате.')

    def _validate_passport(self, passport):
        try:
            passport = int(passport)
        except ValueError:
            raise ValueError('Номер паспорта должен быть только из цифр.')
        if 10000000 <= passport <= 99999999:
            return passport
        raise ValueError('В номере паспорта должно быть 8 цифр.')

    @property
    def fee(self):
        return self.__fee

    def _in_archive(self):
        return self._archive

    def transfer(self, target_account, amount):
        self.withdraw(amount, is_transfer=True)
        target_account.deposit(amount, is_transfer=True)
        op_transfer_to = Operation(Operation.TRANSFER, amount, target_account, amount * (self.fee / 100))
        op_transfer_from = Operation(Operation.TRANSFER, amount, self, amount * (self.fee / 100))
        self.history.append(op_transfer_to)
        target_account.history.append(op_transfer_from)

    def _check_balance(self, amount):
        return amount * (1 + (self.fee / 100)) > self.balance

    def withdraw(self, amount, is_transfer=False):
        if self._check_balance(amount):
            raise ValueError('Недостаточно средств на счете.')
        if self._in_archive():
            raise ValueError('Аккаунт в архиве. Все действия приостановлены.')
        self.balance -= amount * (1 + (self.fee / 100))
        if not is_transfer:
            self.history.append(
                Operation(Operation.WITHDRAW, amount, fee=amount * (self.fee / 100))
            )

    def deposit(self, amount, is_transfer=False):
        if self._in_archive():
            raise ValueError('Аккаунт в архиве. Все действия приостановлены.')
        self.balance += amount
        if not is_transfer:
            op_deposit = Operation(Operation.DEPOSIT, amount)
            self.history.append(op_deposit)

    def full_info(self):

        return f"{self.name} баланс: {self.balance}. Паспорт: {self.passport8}. тел.: {self.phone_number}"

    def __repr__(self):
        return f"{self.name} баланс: {self.balance}."

    def get_history(self):
        return "\n".join(map(str, self.history))

    def to_archive(self):
        if self.balance >= 0:
            self.balance = 0
            self._archive = True
            return
        raise ValueError('Нельзя убрать счет с отрицательным балансом в архив.')

    def restore(self):
        self._archive = False


class CreditAccount(Account):
    def __init__(self, *args, negative_limit=1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.negative_limit = negative_limit
        self.base_transfer_fee = 2
        self.negative_balance_transfer_fee = 5

    @property
    def fee(self):
        if self.balance < 0:
            return self.negative_balance_transfer_fee
        return self.base_transfer_fee

    def _check_balance(self, amount):
        return amount * (1 + (self.fee / 100)) > self.balance + self.negative_limit

    def __repr__(self):
        return '<K> ' + super().__repr__()

    def full_info(self):
        return '<K> ' + super().full_info()


account_ivan = CreditAccount("Ivan", "12385498", "+7900-800-11-22", 3000, negative_limit=1000)
account_petr = Account("Petr", 12345677, "+7900-800-11-33")

account_ivan.deposit(300)

print(account_ivan.full_info())
