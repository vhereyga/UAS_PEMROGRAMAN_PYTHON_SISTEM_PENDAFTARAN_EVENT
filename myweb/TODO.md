# TODO List for Implementing Admin Features, User Event Ownership, and Event Pricing/Stock

## Step 1: Update Database Models
- [x] Update User model to add `is_admin` boolean field (default False)
- [x] Update Event model to add `user_id` (foreign key to User), `harga` (float), `stok` (integer)

## Step 2: Modify Event Routes for Ownership
- [x] Modify add_event route to set event.user_id = session['user_id']
- [x] Modify edit_event route to allow only if session['user_id'] == event.user_id or user.is_admin
- [x] Modify delete_event route to allow only if session['user_id'] == event.user_id or user.is_admin

## Step 3: Add Admin Routes
- [x] Add /admin/users route (list all users)
- [x] Add /admin/users/<id>/edit route (edit user details)
- [x] Add /admin/users/<id>/delete route (delete user)
- [x] Add /admin/events route (admin can manage all events)

## Step 4: Update Templates for New Fields
- [x] Update add_event.html to include harga and stok input fields
- [x] Update edit_event.html to include harga and stok input fields
- [x] Update event_detail.html to display harga and stok

## Step 5: Create New Admin Templates
- [x] Create admin_users.html (list users with edit/delete links)
- [x] Create admin_edit_user.html (form to edit user)
- [x] Create admin_events.html (list all events with admin controls)

## Step 6: Create Admin Account
- [x] Add code to create admin user (username: admin, password: admin123, is_admin=True) if not exists during app startup

## Step 7: Testing and Followup
- [ ] Run the app to update database schema
- [ ] Test user permissions (users can only edit own events)
- [ ] Test admin functions (manage users and all events)
- [ ] Test new event fields (harga, stok)
