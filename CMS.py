import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox, QInputDialog
import sqlite3

# Database initialization
conn = sqlite3.connect('customer_db.sqlite')
c = conn.cursor()

# Create customer table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS customers
             (id INTEGER PRIMARY KEY, name TEXT, password TEXT, balance REAL)''')

# Sample initial data (can be loaded from an existing database)
conn.commit()


class CustomerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Management System")
        self.resize(600, 400)
        self.init_ui()

    def init_ui(self):
        self.menu_label = QLabel("Customer Management System", self)
        self.menu_label.setStyleSheet("font: 75 20pt \"MS Shell Dlg 2\";")
        self.customer_login_button = QPushButton("Customer Login", self)
        self.new_customer_button = QPushButton("New Customer | Register", self)
        self.exit_button = QPushButton("Exit", self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.menu_label)
        vbox.addWidget(self.customer_login_button)
        vbox.addWidget(self.new_customer_button)
        vbox.addWidget(self.exit_button)
        self.setLayout(vbox)

        self.customer_login_button.clicked.connect(self.handle_customer_login)
        self.new_customer_button.clicked.connect(self.handle_new_customer)
        self.exit_button.clicked.connect(self.exit_application)

    def handle_customer_login(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Customer Login")
        dialog.resize(400, 300)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        cust_name_label = QLabel("Customer Name:")
        password_label = QLabel("Password:")
        self.cust_name_entry = QLineEdit()
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(cust_name_label)
        layout.addWidget(self.cust_name_entry)
        layout.addWidget(password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(button_box)

        if dialog.exec_():
            name = self.cust_name_entry.text()
            password = self.password_entry.text()
            customer = self.validate_customer(name, password)
            if customer:
                QMessageBox.information(self, "Welcome", f"Welcome {name}!") 
                self.handle_account_menu(customer)
            else:
                QMessageBox.critical(self, "Invalid Customer", "Invalid customer credentials.")
                self.handle_customer_login()

    def validate_customer(self, name, password):
        c.execute("SELECT * FROM customers WHERE name=? AND password=?", (name, password))
        customer = c.fetchone()
        return customer  # returns None if no matching customer found

    def handle_account_menu(self, customer):

        menu_text = """
        Account Details

        a) Amount Deposit
        b) Amount Withdrawal
        c) Check Balance
        d) Exit
        """
        choice, _ = QInputDialog.getText(self, "Option", menu_text + "\nSelect an option (a, b, c, d):")
        if choice:
            if choice == 'a':  # Deposit
                amount, ok = QInputDialog.getDouble(self, "Deposit Amount", "Enter amount to deposit:")
                if ok and amount > 0:
                    self.deposit_amount(customer[0], amount)
                    QMessageBox.information(self, "Deposit", f"Deposit successful. Current balance: {self.check_balance(customer[0])}")
                    self.handle_account_menu(customer)
                else:
                    QMessageBox.warning(self, "Invalid Amount", "Please enter a valid deposit amount.")
                    self.handle_account_menu(customer)

            elif choice == 'b':  # Withdrawal
                amount, ok = QInputDialog.getDouble(self, "Withdraw Amount", "Enter amount to withdraw:")
                if ok and amount > 0:
                    if self.withdraw_amount(customer[0], amount):
                        QMessageBox.information(self, "Withdrawal", f"Withdrawal successful. Current balance: {self.check_balance(customer[0])}")
                        self.handle_account_menu(customer)
                    else:
                        QMessageBox.warning(self, "Insufficient Balance", "Insufficient balance for withdrawal.")
                        self.handle_account_menu(customer)
                else:
                    QMessageBox.warning(self, "Invalid Amount", "Please enter a valid withdrawal amount.")
                    self.handle_account_menu(customer)

            elif choice == 'c':  # Check Balance
                QMessageBox.information(self, "Balance", f"Your current balance: {self.check_balance(customer[0])}")
                self.handle_account_menu(customer)

            elif choice == 'd':  # Exit
                pass

    def deposit_amount(self, customer_id, amount):
        c.execute("UPDATE customers SET balance = balance + ? WHERE id=?", (amount, customer_id))
        conn.commit()

    def withdraw_amount(self, customer_id, amount):
        c.execute("SELECT balance FROM customers WHERE id=?", (customer_id,))
        current_balance = c.fetchone()[0]
        if amount > current_balance:
            return False  # insufficient balance
        else:
            c.execute("UPDATE customers SET balance = balance - ? WHERE id=?", (amount, customer_id))
            conn.commit()
            return True

    def check_balance(self, customer_id):
        c.execute("SELECT balance FROM customers WHERE id=?", (customer_id,))
        balance = c.fetchone()[0]
        return balance

    def handle_new_customer(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Customer Sign In")
        dialog.resize(400, 300)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        cust_name_label = QLabel("Customer Name:")
        password_label = QLabel("Password:")
        self.new_cust_name_entry = QLineEdit()
        self.new_password_entry = QLineEdit()
        self.new_password_entry.setEchoMode(QLineEdit.Password)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(cust_name_label)
        layout.addWidget(self.new_cust_name_entry)
        layout.addWidget(password_label)
        layout.addWidget(self.new_password_entry)
        layout.addWidget(button_box)

        if dialog.exec_():
            name = self.new_cust_name_entry.text()
            password = self.new_password_entry.text()
            if name and password:
                c.execute("INSERT INTO customers (name, password, balance) VALUES (?, ?, 0)", (name, password))
                conn.commit()
                QMessageBox.information(self, "Success", "New customer registered successfully.")
            else:
                QMessageBox.warning(self, "Incomplete Details", "Please provide both name and password.")

    def exit_application(self):
        QMessageBox.information(self, "Exit", "Exited Application successfully...")
        self.close()

    def closeEvent(self, event):
        conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    customer_app = CustomerApp()
    customer_app.show()
    sys.exit(app.exec_())
