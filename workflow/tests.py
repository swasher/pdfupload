from django.test import TestCase

from workflow.models import Phone

class PhoneTests(TestCase):

    def test_str(self):

        phone = Phone(phone='+380985803239')
        self.assertEquals(str(phone), '+380985803239')