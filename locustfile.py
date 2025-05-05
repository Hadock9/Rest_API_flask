from locust import HttpUser, task, between, SequentialTaskSet
import json
import random
from typing import Optional

class LibraryUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Initialize test data"""
        self.test_books = [
            {
                "title": "Test Book 1",
                "author": "Test Author 1",
                "year": 2024
            },
            {
                "title": "Test Book 2",
                "author": "Test Author 2",
                "year": 2023
            }
        ]
        self.created_book_ids = []
    
    @task(3)
    def get_books(self):
        """Get all books (most common operation)"""
        with self.client.get("/books", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Response is not a list of books")
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def get_single_book(self):
        """Get a single book by ID"""
        # Using a random ID between 1-10 for testing
        book_id = random.randint(1, 10)
        with self.client.get(f"/books/{book_id}", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if all(key in data for key in ["id", "title", "author", "year"]):
                        response.success()
                    else:
                        response.failure("Book data is incomplete")
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            elif response.status_code == 404:
                response.success()  # Book not found is a valid case
            else:
                response.failure(f"Got unexpected status code {response.status_code}")
    
    @task(1)
    def add_book(self):
        """Add a new book"""
        book_data = random.choice(self.test_books)
        headers = {'Content-Type': 'application/json'}
        with self.client.post("/books", 
                            json=book_data,
                            headers=headers,
                            catch_response=True) as response:
            if response.status_code == 201:
                try:
                    data = response.json()
                    if 'id' in data:
                        self.created_book_ids.append(data['id'])
                        response.success()
                    else:
                        response.failure("Response does not contain book ID")
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def delete_book(self):
        """Delete a book if we have created one"""
        if self.created_book_ids:
            book_id = self.created_book_ids.pop(0)  # Remove and get the first created book
            with self.client.delete(f"/books/{book_id}", 
                                  catch_response=True) as response:
                if response.status_code in [200, 204]:
                    response.success()
                else:
                    response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def update_book(self):
        """Update an existing book"""
        if self.created_book_ids:
            book_id = random.choice(self.created_book_ids)
            updated_data = {
                "title": f"Updated Book {random.randint(1, 1000)}",
                "author": f"Updated Author {random.randint(1, 1000)}",
                "year": random.randint(2000, 2024)
            }
            headers = {'Content-Type': 'application/json'}
            with self.client.put(f"/books/{book_id}",
                               json=updated_data,
                               headers=headers,
                               catch_response=True) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if all(key in data for key in ["id", "title", "author", "year"]):
                            response.success()
                        else:
                            response.failure("Updated book data is incomplete")
                    except json.JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                else:
                    response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def search_books(self):
        """Search books by author or title"""
        search_term = random.choice(["Test", "Book", "Author"])
        with self.client.get(f"/books/search?q={search_term}", 
                           catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Search response is not a list")
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                response.failure(f"Got status code {response.status_code}") 