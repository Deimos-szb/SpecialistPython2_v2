EMPLOYEE_PASSWORD = "123"

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


def close_account():
    """
    Закрыть счет клиента.
    Считаем, что оставшиеся на счету деньги были выданы клиенту наличными, при закрытии счета
    """
    pass


def view_accounts_list():
    """
        Отображение всех клиентов банка в виде нумерованного списка
        """
    for nom, acc in enumerate(accounts):
        print(nom, acc)

def view_account_by_passport():
    pass


def view_client_account():
    """
    Узнать состояние своего счета
    """
    pass


def put_account():
    """
    Пополнить счет на указанную сумму.
    Считаем, что клиент занес наличные через банкомат
    """
    pass


def withdraw(account):
    """
    Снять со счета.
    Считаем, что клиент снял наличные через банкомат
    """
    pass


def transfer(account):
    """
    Перевести на счет другого клиента по номеру телефона
    """
    import re
    try:
        amount = int(input('Сколько планируете перевести? '))
    except:
        print("Введена некорректная сумма. Возврат в предыдущее меню.")
        return
    phone = input('Введите номер получателя по маске: +7***-***-**-**\n')
    if re.search(r'\+7\d{3}-\d{3}-\d{2}-\d{2}', phone):
        target_account = search_by_phone(phone)
        if target_account:
            try:
                account.transfer(target_account, amount)
            except ValueError as e:
                print(e)
                print('Возвращаемся в предыдущее меню.')
                return
        else:
            print('Аккаунт с таким номером не найден.')


def create_new_account():
    print("Укажите данные клиента")
    name = input("Имя:")
    passport = input("Номер паспорта: ")
    phone_number = input("Номер телефона: ")
    amount = int(input("Сколько класть на счет: "))
    # TODO: тут создаем новый аккаунт пользователя account = ...
    #   и добавляем его в accounts.append(account)

    accounts.append(
        Account(name, passport, phone_number, amount)
    )


def client_menu(account):
    while True:
        print(f"***********Меню клиента {account.name}*************")
        print("1. Состояние счета")
        print("2. Пополнить счет")
        print("3. Снять со счета")
        print("4. Перевести деньги другому клиенту банка")
        print("5. Exit")
        choice = input(":")
        if choice == "1":
            view_client_account(account)
        elif choice == "2":
            put_account(account)
        elif choice == "3":
            withdraw(account)
        elif choice == "4":
            transfer(account)
        elif choice == "5":
            return
    # input("Press Enter")


def employee_menu():
    while True:
        print("***********Меню сотрудника*************")
        print("1. Создать новый счет")
        print("2. Закрыть счет")
        print("3. Посмотреть список счетов")
        print("4. Посмотреть счет по номеру паспорта")
        print("5. Exit")
        choice = input(":")
        if choice == "1":
            create_new_account()
        elif choice == "2":
            close_account()
        elif choice == "3":
            view_accounts_list()
        elif choice == "4":
            view_account_by_passport()
        elif choice == "5":
            return


def employee_access():
    """
    Проверяет доступ сотрудника банка, запрашивая пароль
    """
    password = input("Пароль: ")
    if password == EMPLOYEE_PASSWORD:
        return True
    return False


def client_access(accounts):
    """
    Находит аккаунт с введеным номером паспорта
    Или возвращает False, если аккаунт не найден
    """
    try:
        passport = int(input("Номер паспорта: "))
    except ValueError:
        return False
    for account in accounts:
        if passport == account.passport8:
            return account

    return False


def start_menu():
    while True:
        print("Укажите вашу роль:")
        print("1. Сотрудник банка")
        print("2. Клиент")
        print("3. Завершить работу")

        choice = input(":")
        if choice == "3":
            break
        elif choice == "1":
            if employee_access():
                employee_menu()
            else:
                print("Указан неверный пароль, укажите роль и повторите попытку...")
        elif choice == "2":
            account = client_access(accounts)
            if account:
                client_menu(account)
            else:
                print("Указан несуществующий пасспорт, укажите роль и повторите попытку...")
        else:
            print("Указан некорректный пункт меню, повторите выбор...")

def search_by_phone(phone):
    for acc in accounts:
        if acc.phone_number == phone:
            return acc
    return None


if __name__ == "__main__":
    accounts = []
    start_menu()
