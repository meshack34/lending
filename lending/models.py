from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# -------------------------------
# 1. Custom User with Roles
# -------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("OFFICER", "Loan Officer"),
        ("MEMBER", "Member"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="MEMBER")

    def is_admin(self):
        return self.role == "ADMIN"

    def is_officer(self):
        return self.role == "OFFICER"

    def is_member(self):
        return self.role == "MEMBER"

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------------------
# 2. Member Profile
# -------------------------------
class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    alternative_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.national_id})"


# -------------------------------
# 3. Loan Policies (Admin-defined)
# -------------------------------
class LoanPolicy(models.Model):
    name = models.CharField(max_length=100)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # flat rate (% per year)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_term_months = models.PositiveIntegerField()

    def __str__(self):
        return self.name


# -------------------------------
# 4. Loans
# -------------------------------
class Loan(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("DISBURSED", "Disbursed"),
        ("CLOSED", "Closed"),
    ]

    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name="loans")
    policy = models.ForeignKey(LoanPolicy, on_delete=models.SET_NULL, null=True, blank=True)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    term_months = models.PositiveIntegerField()
    purpose = models.TextField(blank=True, null=True)

    # snapshot from policy
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_payable = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(blank=True, null=True)
    disbursed_at = models.DateTimeField(blank=True, null=True)

    def calculate_total_payable(self):
        """Flat rate: total = principal + (principal * rate * time/12)."""
        interest = self.principal_amount * (self.interest_rate / 100) * (self.term_months / 12)
        return self.principal_amount + interest

    def save(self, *args, **kwargs):
        if not self.total_payable:
            self.total_payable = self.calculate_total_payable()
        if not self.balance:
            self.balance = self.total_payable
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.id} - {self.member.user.username} ({self.status})"


# -------------------------------
# 5. Repayments (M-Pesa)
# -------------------------------
class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayments")
    transaction_id = models.CharField(max_length=100, unique=True)
    payer_phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update loan balance after saving repayment
        self.loan.balance -= self.amount
        if self.loan.balance <= 0:
            self.loan.balance = 0
            self.loan.status = "CLOSED"
        self.loan.save()


# -------------------------------
# 6. Reports (basic log)
# -------------------------------
class ReportLog(models.Model):
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    report_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.report_type} by {self.generated_by} on {self.created_at}"
