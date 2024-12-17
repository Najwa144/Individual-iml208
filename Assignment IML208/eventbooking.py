import tkinter as tk
from tkinter import messagebox
import sqlite3

# Connect to SQLite database (creates if not exists)
conn = sqlite3.connect('event_booking.db')
c = conn.cursor()

# Create events table if not exists
c.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        seats_available INTEGER
    )
''')

# Create bookings table if not exists
c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        name TEXT,
        seats_booked INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id)
    )
''')

conn.commit()

# Add a new event 
def add_event():
    event_name = entry_event_name.get()
    event_date = entry_event_date.get()
    seats_available = entry_seats_available.get()

    if event_name and event_date and seats_available.isdigit():
        seats_available = int(seats_available)
        c.execute("INSERT INTO events (name, date, seats_available) VALUES (?, ?, ?)",
                  (event_name, event_date, seats_available))
        conn.commit()
        entry_event_name.delete(0, tk.END)
        entry_event_date.delete(0, tk.END)
        entry_seats_available.delete(0, tk.END)
        display_events()
        messagebox.showinfo("Success", "Event added successfully!")

# Display all events
def display_events():
    listbox_events.delete(0, tk.END)
    c.execute("SELECT * FROM events")
    rows = c.fetchall()
    for row in rows:
        listbox_events.insert(tk.END, f"{row[0]}: {row[1]} - {row[2]} - {row[3]} seats available")

# Update event details 
def update_event():
    selected_event = listbox_events.curselection()
    if selected_event:
        event_id = listbox_events.get(selected_event).split(":")[0]
        new_seats = entry_seats_available.get()
        
        if new_seats.isdigit():
            c.execute("UPDATE events SET seats_available = ? WHERE id = ?", 
                      (int(new_seats), event_id))
            conn.commit()
            entry_seats_available.delete(0, tk.END)
            display_events()
            messagebox.showinfo("Success", "Event updated successfully!")

# Delete an event 
def delete_event():
    selected_event = listbox_events.curselection()
    if selected_event:
        event_id = listbox_events.get(selected_event).split(":")[0]
        c.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        display_events()
        messagebox.showinfo("Success", "Event deleted successfully!")
    
# Book tickets 
def book_tickets():
    selected_event = listbox_events.curselection()
    if selected_event:
        event_id = listbox_events.get(selected_event).split(":")[0]
        user_name = entry_user_name.get()
        seats_to_book = entry_seats_to_book.get()

        if user_name and seats_to_book.isdigit():
            seats_to_book = int(seats_to_book)

            c.execute("SELECT seats_available FROM events WHERE id = ?", (event_id,))
            available_seats = c.fetchone()[0]

            if seats_to_book <= available_seats:
                c.execute("INSERT INTO bookings (event_id, name, seats_booked) VALUES (?, ?, ?)", 
                          (event_id, user_name, seats_to_book))
                c.execute("UPDATE events SET seats_available = ? WHERE id = ?", 
                          (available_seats - seats_to_book, event_id))
                conn.commit()
                entry_user_name.delete(0, tk.END)
                entry_seats_to_book.delete(0, tk.END)
                display_events()
                messagebox.showinfo("Success", "Tickets booked successfully!")
            
# Cancel booking 
def cancel_booking():
    selected_event = listbox_events.curselection()
    if selected_event:
        event_id = listbox_events.get(selected_event).split(":")[0]
        user_name = entry_user_name.get()

        if user_name:
            c.execute("SELECT seats_booked FROM bookings WHERE event_id = ? AND name = ?", (event_id, user_name))
            booking = c.fetchone()

            if booking:
                seats_booked = booking[0]
                c.execute("DELETE FROM bookings WHERE event_id = ? AND name = ?", (event_id, user_name))
                c.execute("UPDATE events SET seats_available = seats_available + ? WHERE id = ?", 
                          (seats_booked, event_id))
                conn.commit()
                entry_user_name.delete(0, tk.END)
                display_events()
                messagebox.showinfo("Success", "Booking canceled successfully!")
           
# Setting up the GUI window
root = tk.Tk()
root.title("Event Booking System")

# Event Management Section
label_event_name = tk.Label(root, text="Event Name:")
label_event_name.pack(pady=5)

entry_event_name = tk.Entry(root, width=40)
entry_event_name.pack(pady=5)

label_event_date = tk.Label(root, text="Event Date:")
label_event_date.pack(pady=5)

entry_event_date = tk.Entry(root, width=40)
entry_event_date.pack(pady=5)

label_seats_available = tk.Label(root, text="Seats Available:")
label_seats_available.pack(pady=5)

entry_seats_available = tk.Entry(root, width=40)
entry_seats_available.pack(pady=5)

button_add_event = tk.Button(root, text="Add Event", width=20, command=add_event)
button_add_event.pack(pady=5)

button_update_event = tk.Button(root, text="Update Event", width=20, command=update_event)
button_update_event.pack(pady=5)

button_delete_event = tk.Button(root, text="Delete Event", width=20, command=delete_event)
button_delete_event.pack(pady=5)

# Display events section
listbox_events = tk.Listbox(root, height=10, width=50)
listbox_events.pack(pady=5)

# Booking Section
label_user_name = tk.Label(root, text="Your Name:")
label_user_name.pack(pady=5)

entry_user_name = tk.Entry(root, width=40)
entry_user_name.pack(pady=5)

label_seats_to_book = tk.Label(root, text="Seats to Book:")
label_seats_to_book.pack(pady=5)

entry_seats_to_book = tk.Entry(root, width=40)
entry_seats_to_book.pack(pady=5)

button_book_tickets = tk.Button(root, text="Book Tickets", width=20, command=book_tickets)
button_book_tickets.pack(pady=5)

button_cancel_booking = tk.Button(root, text="Cancel Booking", width=20, command=cancel_booking)
button_cancel_booking.pack(pady=5)

# Display initial events
display_events()

# Run the Tkinter event loop
root.mainloop()

# Close the database connection when the app is closed
conn.close()
