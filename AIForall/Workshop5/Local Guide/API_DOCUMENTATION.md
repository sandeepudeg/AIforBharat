# Pune Knowledge Base - API Documentation

## Overview

The Pune Knowledge Base API provides RESTful endpoints for accessing articles, categories, search functionality, and chat services. All endpoints return JSON responses with consistent formatting.

## Base URL

```
http://localhost:5000/api
```

## Response Format

All API responses follow this standard format:

### Success Response
```json
{
  "success": true,
  "data": {},
  "count": 0
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid input or validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Endpoints

### 1. Search Articles

**Endpoint:** `GET /api/search`

**Description:** Search across all articles with optional category filtering.

**Query Parameters:**
- `q` (required, string): Search query (minimum 2 characters)
- `category` (optional, string): Filter results by category ID

**Example Requests:**

```bash
# Basic search
curl "http://localhost:5000/api/search?q=pune"

# Search with category filter
curl "http://localhost:5000/api/search?q=food&category=food"

# Search with limit
curl "http://localhost:5000/api/search?q=culture&category=culture"
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "misal_pav",
      "title": "Misal Pav",
      "category": "food",
      "description": "A spicy curry made with sprouted moong beans...",
      "content": "Full article content here...",
      "tags": ["food", "street-food", "breakfast"],
      "relevance_score": 95
    }
  ],
  "count": 1,
  "query": "pune"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Search query must be at least 2 characters long"
}
```

---

### 2. Get All Categories

**Endpoint:** `GET /api/categories`

**Description:** Retrieve all available categories with article counts.

**Example Request:**

```bash
curl "http://localhost:5000/api/categories"
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "food",
      "name": "Food & Street Culture",
      "description": "Explore Pune's culinary delights...",
      "article_count": 5
    },
    {
      "id": "culture",
      "name": "Puneri Culture & Humor",
      "description": "Discover the unique culture of Pune...",
      "article_count": 3
    }
  ],
  "count": 16
}
```

---

### 3. Get Specific Category

**Endpoint:** `GET /api/categories/<category_id>`

**Description:** Retrieve detailed information about a specific category including all articles.

**Path Parameters:**
- `category_id` (required, string): The category identifier (e.g., "food", "culture")

**Example Request:**

```bash
curl "http://localhost:5000/api/categories/food"
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "food",
    "name": "Food & Street Culture",
    "description": "Explore Pune's culinary delights...",
    "articles": [
      {
        "id": "misal_pav",
        "title": "Misal Pav",
        "description": "A spicy curry...",
        "tags": ["food", "breakfast"]
      }
    ],
    "article_count": 5
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Category not found"
}
```

---

### 4. Get Category Articles

**Endpoint:** `GET /api/categories/<category_id>/articles`

**Description:** Retrieve all articles in a specific category.

**Path Parameters:**
- `category_id` (required, string): The category identifier

**Example Request:**

```bash
curl "http://localhost:5000/api/categories/food/articles"
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "misal_pav",
      "title": "Misal Pav",
      "category": "food",
      "description": "A spicy curry...",
      "content": "Full content...",
      "tags": ["food", "breakfast"],
      "related_articles": ["jalebi", "poha"]
    }
  ],
  "count": 5
}
```

---

### 5. Get Article Details

**Endpoint:** `GET /api/articles/<article_id>`

**Description:** Retrieve full details of a specific article including related articles.

**Path Parameters:**
- `article_id` (required, string): The article identifier (e.g., "misal_pav")

**Example Request:**

```bash
curl "http://localhost:5000/api/articles/misal_pav"
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "misal_pav",
    "title": "Misal Pav",
    "category": "food",
    "description": "A spicy curry made with sprouted moong beans...",
    "content": "Full article content with detailed information...",
    "tags": ["food", "street-food", "breakfast"],
    "related_articles": ["jalebi", "poha"],
    "related_articles_data": [
      {
        "id": "jalebi",
        "title": "Jalebi",
        "description": "A sweet spiral-shaped dessert..."
      }
    ]
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Article not found"
}
```

---

### 6. Chat Endpoint

**Endpoint:** `POST /api/chat`

**Description:** Send a message to the chat assistant and receive a response with relevant articles.

**Request Body:**
```json
{
  "message": "Tell me about Pune's food culture"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:5000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the best places to visit in Pune?"}'
```

**Success Response (200):**
```json
{
  "success": true,
  "response": "Pune has many wonderful places to visit! Here are some recommendations...",
  "articles": [
    {
      "id": "article_id",
      "title": "Article Title",
      "description": "Article description...",
      "category": "places"
    }
  ]
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Message cannot be empty"
}
```

---

## Error Codes & Messages

### Validation Errors

| Error | Status | Message |
|-------|--------|---------|
| Empty search query | 400 | "Search query cannot be empty" |
| Query too short | 400 | "Search query must be at least 2 characters long" |
| Query too long | 400 | "Search query cannot exceed 200 characters" |
| Invalid category ID | 400 | "Invalid category ID format" |
| Invalid article ID | 400 | "Invalid article ID format" |
| Empty chat message | 400 | "Message cannot be empty" |
| Message too long | 400 | "Message cannot exceed 1000 characters" |

### Not Found Errors

| Error | Status | Message |
|-------|--------|---------|
| Category not found | 404 | "Category not found" |
| Article not found | 404 | "Article not found" |

### Server Errors

| Error | Status | Message |
|-------|--------|---------|
| Internal error | 500 | "Internal server error" |

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting to prevent abuse.

---

## Authentication

Currently, the API does not require authentication. For production use, consider implementing API key authentication or OAuth.

---

## Examples

### Example 1: Search for Food Articles

```bash
curl "http://localhost:5000/api/search?q=misal&category=food"
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "misal_pav",
      "title": "Misal Pav",
      "category": "food",
      "description": "A spicy curry made with sprouted moong beans...",
      "relevance_score": 98
    }
  ],
  "count": 1,
  "query": "misal"
}
```

### Example 2: Get All Categories

```bash
curl "http://localhost:5000/api/categories"
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "food",
      "name": "Food & Street Culture",
      "description": "Explore Pune's culinary delights...",
      "article_count": 5
    },
    {
      "id": "culture",
      "name": "Puneri Culture & Humor",
      "description": "Discover the unique culture of Pune...",
      "article_count": 3
    }
  ],
  "count": 16
}
```

### Example 3: Chat with Assistant

```bash
curl -X POST "http://localhost:5000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Puneri culture"}'
```

Response:
```json
{
  "success": true,
  "response": "Puneri culture is known for its unique humor and direct communication style...",
  "articles": [
    {
      "id": "puneri_patya",
      "title": "Puneri Patya",
      "description": "Sarcastic signboards that are a hallmark of Pune...",
      "category": "culture"
    }
  ]
}
```

---

## Best Practices

1. **Always validate input** - Check query parameters before making requests
2. **Handle errors gracefully** - Check the `success` field in responses
3. **Use appropriate HTTP methods** - GET for retrieval, POST for actions
4. **Cache responses** - The API implements server-side caching for performance
5. **Respect rate limits** - Implement client-side throttling for high-volume requests

---

## Support

For issues or questions about the API, please refer to the README.md or contact the development team.
