import pickle
from collections import UserDict
from datetime import datetime, timedelta

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # return new AddressBook


class CheckPhoneNumber(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit():
           raise CheckPhoneNumber(f'Phone {value} is not digit') 
        elif len(value) != 10:
            raise CheckPhoneNumber(f'Phone {value} > 10 digits')
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value,"%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_phone(self,phone):
        self.phones.append(Phone(phone))
    
    def remove_phone(self, phone):
        if phone in [p.value for p in self.phones]:
            self.phones = [p for p in self.phones if p.value != phone]
    
    def remove_all_phones(self):
        self.phones = []

    def edit_phone(self, old_phone, new_phone):
        try:
            Phone(new_phone)  
        except ValueError as e:
            return str(e)
        
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def find_phone(self,phone):
        try:
            found_phone = next(item for item in self.phones if item.value == phone)
            return found_phone
        except Exception as e:
            return str(e)
        
    def add_birthday(self,birthday_date):
        self.birthday = Birthday(birthday_date)


class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record
   
    def find(self,record):
        return self.data.get(record)
    
    def delete(self,record):
        for key in list(self.keys()):
            if key == record:
                del self[key]

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today()
        for name, record in self.data.items():
           if record.birthday is None:
            pass
           else:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = record.birthday.value.replace(year=today.year+1)
                    
                if 0 <= (birthday_this_year - today).days <= days:
                    birthday_this_year = self.adjust_for_weekend(birthday_this_year)
                    upcoming_birthdays.append({"Contact": name, "upcoming birthday":birthday_this_year.strftime("%d.%m.%Y")})
        return upcoming_birthdays
  
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Incorrect value."
        except KeyError:
            return "Enter the argument for the command"
        except IndexError:
            return "Enter the argument for the command"

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args
    
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact changed."
    if record is None:
        message = "Contact not found."
    else:
        record.remove_all_phones() # clean all phones
        record.add_phone(phone)
    return message

@input_error
def get_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact not found!"
    else:
        return f"{record}"
    
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_date, *_ = args
    record = book.find(name)
    message = "Contact birthday updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added. Birthday updated."
    if birthday_date:
        record.add_birthday(birthday_date)
    return message

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact not found!"
    else:
        if not record.birthday is None:
            return f"{record.birthday.value.strftime("%d.%m.%Y")}"
        else:
            return None


def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()

def main():

    # book = AddressBook()
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(get_phone(args, book))

        elif command == "all":
            for name, record in book.data.items():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()