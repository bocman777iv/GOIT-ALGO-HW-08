import re
from datetime import datetime, timedelta
import pickle

PHONE_PATTERN = re.compile(r'^\+?\d{10}$')

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD-MM-YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not PHONE_PATTERN.match(phone):
            raise ValueError("Invalid phone number format.")
        self.phones.append(phone)

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str).value

class AddressBook(dict):
    def add_record(self, record):
        self[record.name.value] = record

    def find(self, name):
        return self.get(name)

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, IndexError, ValueError) as e:
            if isinstance(e, ValueError) and str(e) in ["Enter name and phone please", "Invalid phone number format."]:
                return str(e)
            elif isinstance(e, KeyError):
                return "Enter name!"
            elif isinstance(e, IndexError):
                return "Enter name and phone number!"
            else:
                return str(e)
    return inner

@input_error
def add_contact(args, book: AddressBook):
    if len(args.split()) < 2:
        raise ValueError("Enter name and phone please")

    name, phone, *_ = args.split()
    if not PHONE_PATTERN.match(phone):
        raise ValueError("Invalid phone number format.")

    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    save_data(book)
    return message

@input_error
def change_contact(user_input, book: AddressBook):
    if len(user_input.split()) < 2:
        raise ValueError("Enter name and phone please")

    name, new_phone_number, *_ = user_input.split()
    if not PHONE_PATTERN.match(new_phone_number):
        raise ValueError("Invalid phone number format.")

    record = book.find(name)
    if record:
        record.phones = [new_phone_number]
        save_data(book)
        return "Contact updated!."
    else:
        return "Contact not found!."

@input_error
def show_phone(user_input, book: AddressBook):
    name = user_input.strip()
    record = book.find(name)
    if record:
        return ', '.join(record.phones)
    else:
        return "Contact not found!."

def show_all(book: AddressBook):
    if book:
        for record in book.values():
            phones = ', '.join(record.phones)
            birthday = record.birthday.strftime('%d-%m-%Y') if record.birthday else 'No birthday set'
            print(f"{record.name.value}: Phones: {phones}, Birthday: {birthday}")
    else:
        print("No contacts!.")

@input_error
def add_birthday(user_input, book: AddressBook):
    name, birthday_str, *_ = user_input.split()
    record = book.find(name)
    if record:
        record.add_birthday(birthday_str)
        save_data(book)
        return "Birthday added!."
    else:
        return "Contact not found!."

@input_error
def show_birthday(user_input, book: AddressBook):
    name = user_input.strip()
    record = book.find(name)
    if record:
        birthday = record.birthday
        return birthday.strftime('%d-%m-%Y') if birthday else "No birthday set!."
    else:
        return "Contact not found!."

@input_error
def show_upcoming_birthdays(book: AddressBook):
    upcoming_birthdays = []
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    for record in book.values():
        birthday = record.birthday
        if birthday:
            this_year_birthday = birthday.replace(year=today.year)
            if today <= this_year_birthday <= next_week:
                upcoming_birthdays.append((record.name.value, this_year_birthday))
    if upcoming_birthdays:
        for name, date in upcoming_birthdays:
            print(f"{name}: {date.strftime('%d-%m-%Y')}")
    else:
        print("No upcoming birthdays!.")

def main():
    book = load_data()
    
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")

        if not user_input.strip():
            print("Empty input. Please enter a command.")
            continue

        command, *args = user_input.split(maxsplit=1)
        args = ' '.join(args) if args else ''

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            show_upcoming_birthdays(book)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
