# Import our database helper file and our login helper file
from app import database as db
from app.services import auth_tools
# Give back the list of current managers (each one is a dictionary)
def list_managers():
    # SELECT reads every user whose role is manager, sorted by name
    rows = db.fetch_all(
        "SELECT user_id, name, email, created_at FROM users WHERE role = 'manager' ORDER BY name;"
    )

    # Start with an empty list
    managers = []

    # Go through the rows one at a time
    for row in rows:
        # Turn the row into a dictionary with clear names (the date is cut to "2026-10-29")
        managers.append({"user_id": row[0], "name": row[1], "email": row[2], "since": str(row[3])[:10]})

    # Give the list back
    return managers


# Give back the list of pending manager invites
def list_pending_invites():
    # SELECT reads every pending invite and the name of the HR who made it (LEFT JOIN keeps the invite even if the name is missing)
    rows = db.fetch_all(
        "SELECT i.invite_id, i.email, i.created_at, u.name FROM role_invites i "
        "LEFT JOIN users u ON i.invited_by = u.user_id "
        "WHERE i.role = 'manager' AND i.status = 'pending' ORDER BY i.invite_id DESC;"
    )

    # Start with an empty list
    invites = []

    # Go through the rows one at a time
    for row in rows:
        # Turn the row into a dictionary with clear names (the date is cut to "2026-10-29 14:05")
        invites.append({"invite_id": row[0], "email": row[1], "created": str(row[2])[:16], "invited_by": row[3]})

    # Give the list back
    return invites


# Give manager access to a Gmail. Give back a dictionary: ok (True/False), code, message
def invite_manager(hr_user_id, email):
    # Look if this Gmail already has an account
    user = auth_tools.get_user_by_email(email)

    # An HR account cannot also be a manager
    if user is not None and user["role"] == "hr":
        return {"ok": False, "code": "", "message": "This Gmail belongs to an HR account. HR cannot also be a manager."}

    # Already a manager, so nothing to do
    if user is not None and user["role"] == "manager":
        return {"ok": False, "code": "", "message": "This person is already a manager."}

    # Open one connection, so the changes below are saved together or not at all
    connection = db.get_connection()
    cursor = connection.cursor()

    # CASE 1: the person already has a verified account, so the Gmail was already proven
    if user is not None and user["email_verified"]:
        # UPDATE changes the role to manager (only if the person is a candidate right now)
        cursor.execute(
            "UPDATE users SET role = 'manager' WHERE user_id = %s AND role = 'candidate' AND email_verified = TRUE;",
            (user["user_id"],),
        )

        # INSERT writes the invite as already accepted, so there is a record of who gave the access
        cursor.execute(
            "INSERT INTO role_invites (email, role, invited_by, status) VALUES (%s, 'manager', %s, 'accepted');",
            (email, hr_user_id),
        )

        # Save both changes for good, then close
        connection.commit()
        cursor.close()
        connection.close()

        # Tell the caller what happened
        return {"ok": True, "code": "promoted", "message": ""}

    # CASE 2: no account yet, or the account is not verified yet. First check for an older pending invite
    cursor.execute(
        "SELECT invite_id FROM role_invites WHERE email = %s AND role = 'manager' AND status = 'pending' LIMIT 1;",
        (email,),
    )
    older_invite = cursor.fetchone()

    # If there is already a pending invite, do not make a second one
    if older_invite is not None:
        cursor.close()
        connection.close()
        return {"ok": False, "code": "", "message": "This Gmail already has a pending invite."}

    # INSERT saves the new pending invite. The role changes when this Gmail verifies its code
    cursor.execute(
        "INSERT INTO role_invites (email, role, invited_by, status) VALUES (%s, 'manager', %s, 'pending');",
        (email, hr_user_id),
    )

    # Save the change for good, then close
    connection.commit()
    cursor.close()
    connection.close()

    # Tell the caller what happened
    return {"ok": True, "code": "invited", "message": ""}


# Remove manager access: the person becomes a candidate again. Give back True if it worked
def remove_manager(user_id):
    # Open one connection, so the changes below are saved together or not at all
    connection = db.get_connection()
    cursor = connection.cursor()

    # UPDATE changes the role back to candidate, only if the person is a manager. RETURNING gives back the Gmail
    cursor.execute(
        "UPDATE users SET role = 'candidate' WHERE user_id = %s AND role = 'manager' RETURNING email;",
        (user_id,),
    )
    row = cursor.fetchone()

    # If no row came back, this person is not a manager, so change nothing
    if row is None:
        connection.rollback()
        cursor.close()
        connection.close()
        return False

    # UPDATE closes the old invites of this Gmail, so the access cannot come back by itself
    cursor.execute(
        "UPDATE role_invites SET status = 'removed' WHERE email = %s AND role = 'manager' "
        "AND status IN ('accepted', 'pending');",
        (row[0],),
    )

    # Save both changes for good, then close
    connection.commit()
    cursor.close()
    connection.close()
    return True


# Cancel a pending invite. Give back True if an invite was cancelled
def cancel_invite(invite_id):
    # UPDATE closes the invite, only if it is still pending
    rows_changed = db.execute(
        "UPDATE role_invites SET status = 'removed' WHERE invite_id = %s AND role = 'manager' AND status = 'pending';",
        (invite_id,),
    )

    # True means one row was changed
    return rows_changed == 1