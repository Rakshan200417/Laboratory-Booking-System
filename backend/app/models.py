class User:
    def __init__(self, user_id, e_id, name, email, phone, department, role_name, status="Active"):
        self.user_id = user_id
        self.e_id = e_id
        self.name = name
        self.email = email
        self.phone = phone
        self.department = department
        self.role_name = role_name
        self.status = status

    def get_role_name(self):
        return self.role_name

    def describe(self):
        return f"{self.name} ({self.e_id}) - {self.role_name}"


class Student(User):
    def __init__(self, user_id, e_id, name, email, phone, department, year_of_study, index_number, program, batch, status="Active"):
        super().__init__(user_id, e_id, name, email, phone, department, "Student", status)
        self.year_of_study = year_of_study
        self.index_number = index_number
        self.program = program
        self.batch = batch


class Lecturer(User):
    def __init__(self, user_id, e_id, name, email, phone, department, employee_id, designation, status="Active"):
        super().__init__(user_id, e_id, name, email, phone, department, "Lecturer", status)
        self.employee_id = employee_id
        self.designation = designation


class Administrator(User):
    def __init__(self, user_id, e_id, name, email, phone, department, status="Active"):
        super().__init__(user_id, e_id, name, email, phone, department, "Administrator", status)

    def can_approve_bookings(self):
        return True


class Laboratory:
    def __init__(self, laboratory_id, name, code, location, capacity, description, status="Available"):
        self.laboratory_id = laboratory_id
        self.name = name
        self.code = code
        self.location = location
        self.capacity = capacity
        self.description = description
        self.status = status

    def is_bookable(self):
        return self.status == "Available"


class Equipment:
    def __init__(self, equipment_id, laboratory_id, name, quantity_total, quantity_available, condition, status="Available"):
        self.equipment_id = equipment_id
        self.laboratory_id = laboratory_id
        self.name = name
        self.quantity_total = quantity_total
        self.quantity_available = quantity_available
        self.condition = condition
        self.status = status


class Booking:
    def __init__(self, booking_id, user_id, laboratory_id, purpose, booking_date, start_time, end_time, status="Pending"):
        self.booking_id = booking_id
        self.user_id = user_id
        self.laboratory_id = laboratory_id
        self.purpose = purpose
        self.booking_date = booking_date
        self.start_time = start_time
        self.end_time = end_time
        self.status = status

    def overlaps_with(self, other_date, other_start, other_end):
        if self.booking_date != other_date:
            return False
        return self.start_time < other_end and self.end_time > other_start
