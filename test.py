from contacts.views import ContactListCreateAPIView

contact = {
    'name': 'Akul',
    'phone': 9548372727
}


create = ContactListCreateAPIView.create()
create(contact)
