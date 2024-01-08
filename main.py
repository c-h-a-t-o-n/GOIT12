from datetime import datetime
from collections import UserDict
import json


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value


    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self._validate(value):
            self.__value = value
        else:
            raise ValueError(f"Invalid value for {self.__class__.__name__}.")


    def _validate(self, value):
        return True  # Базова функція валідації, яку можна перевизначити у підкласах


    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value=""):
        super().__init__(value)


    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if value:
            if type(value) == str and len(value) == 10 and value.isdigit():
                self.__value = value
            else:
                raise ValueError("Invalid phone number format.")
        else:
            self.__value = ""


    def validate(self, value):
        if value:
            return isinstance(value, str) and len(value) == 10 and value.isdigit()
        return True


class Birthday(Field):
    def __init__(self, value=""):
        super().__init__(value)


    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if value:
            try:
                self.__value = datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                raise ValueError("Invalid date format. Please use DD.MM.YYYY.")
        else:
            self.__value = ""


    def __str__(self):
        return self.value.strftime("%d.%m.%Y") if self.value else ""


    def validate(self, value):
        if value:
            try:
                datetime.strptime(value, "%d.%m.%Y")
                return True
            except ValueError:
                return False


    def __str__(self):
        return self.value.strftime("%d.%m.%Y") if self.value else ""


class Record:
    def __init__(self, name, phones=None, birthday=""):
        self.name = Name(name)
        self.phones = [Phone(phone) for phone in (phones or [])]
        self.birthday = Birthday(birthday)


    def add_phone(self, phone):
        if phone not in map(lambda item: item.value, self.phones):
            self.phones.append(Phone(phone))
        return self


    def remove_phone(self, phone):
        self.phones = [item for item in self.phones if item.value != phone]
        return self


    def edit_phone(self, old_phone, new_phone):
        for item in self.phones:
            if item.value == old_phone:
                item.value = new_phone
                return self
        raise ValueError("Phone number not found.")


    def find_phone(self, phone):
        return next((item for item in self.phones if item.value == phone), None)


    def set_birthday(self, birthday):
        self.birthday.value = birthday
        return self


    def days_to_birthday(self):
        if self.birthday.value:
            today = datetime.today()
            next_birthday_date = self.birthday.value.replace(year=today.year)

            if today > next_birthday_date:
                next_birthday_date = next_birthday_date.replace(year=today.year + 1)

            days_left = (next_birthday_date - today).days
            return days_left
        return None


    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.records_per_page = 3
        self.current_record = 0


    def add_record(self, record: Record):
        if self.data.get(record.name.value, "") == "":
            self.data[record.name.value] = record
        return self


    def find(self, name: str):
        return self.data.get(name, None)


    def delete(self, name: str):
        self.data.pop(name, None)
        return self


    def iterator(self, batch_size=None):
        batch_size = batch_size or self.records_per_page
        records = list(self.data.values())
        for i in range(0, len(records), batch_size):
            yield records[i:i + batch_size]


    def save_to_file(self, filename="address_book.json"):
        with open(filename, 'w') as file:
            data = {
                'records_per_page': self.records_per_page,
                'current_record': self.current_record,
                'data': {name: record.__dict__ for name, record in self.data.items()}
            }
            json.dump(data, file)


    def load_from_file(self, filename="address_book.json"):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.records_per_page = data['records_per_page']
                self.current_record = data['current_record']
                self.data = {name: Record(**record_data) for name, record_data in data['data'].items()}
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Ігнорує, якщо файл не існує або пошкоджений


    def search(self, term):
        term = term.lower()
        results = []
        for record in self.data.values():
            if term in record.name.value.lower() or any(term in phone.value for phone in record.phones):
                results.append(record)
        return results
    

def main():
    # Завантажує існуючу адресну книгу з файлу
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John", ["3333333333", "4444444444"], "18.02.1990")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John в адресну книгу
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    jane_record.set_birthday("10.03.1970")
    jane_record.set_birthday("11.03.1970")
    book.add_record(jane_record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Вивід: Contact name: John, phones: 3333333333; 4444444444; 1112223333; 5555555555, birthday: 18.02.1990
    print(john.name.value + ": " + john.find_phone("5555555555").value)

    print(jane_record)

    print("\n----------------------\n")

    # Виведення записів із посторінковим висновком
    for i, batch in enumerate(book.iterator(batch_size=2), 1):
        for record in batch:
            print(record)
            if i < len(book.data):
                print("--------- Press 'Enter' to continue ---------")
                _ = input()

    
    book.save_to_file()
    book.load_from_file()

    # Пошук контактів
    search_term = input("Enter search term: ")
    search_results = book.search(search_term)
    if search_results:
        print("Search results:")
        for result in search_results:
            print(result)
    else:
        print("No matching results.")


if __name__ == "__main__":
    main()