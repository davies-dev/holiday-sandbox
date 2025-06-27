# Tag Management in Study Librarian

## Overview

The Study Librarian application now includes comprehensive tag management functionality that allows you to create tags and assign them to study documents in your library. This feature helps organize and categorize your study materials for easier retrieval and analysis.

## Features

### 1. Tag Creation
- Create new tags with descriptive names (e.g., "DelayedCBetOOP", "3BetBluff", "RiverBluff")
- Tags are stored in the database with optional descriptions
- Duplicate tag names are prevented

### 2. Document Tagging
- Assign multiple tags to any study document
- Remove tags from documents as needed
- View all tags assigned to a selected document

### 3. User Interface
- **Left Panel**: Lists all study documents with their titles and file paths
- **Right Panel**: Shows tags assigned to the currently selected document
- **Paned Window Layout**: Resizable panels for optimal workspace usage

## How to Use

### Starting the Application
```bash
python librarian_app.py
```

### Creating Tags
1. Click the "Create New Tag" button in the right panel
2. Enter a tag name (e.g., "DelayedCBetOOP")
3. Click OK to create the tag

### Assigning Tags to Documents
1. Select a document from the left panel
2. Click "Assign Tag" in the right panel
3. Choose a tag from the dropdown list
4. Click OK to assign the tag

### Removing Tags from Documents
1. Select a document from the left panel
2. Select the tag you want to remove in the right panel
3. Click "Remove Tag"
4. Confirm the removal

### Adding New Documents
1. Click "Add New Document" in the left panel
2. Select a markdown file from your file system
3. Enter a title for the document
4. The document will be added to your library

## Database Schema

The tag management system uses three main tables:

### `study_tags`
- `id`: Primary key
- `tag_name`: Unique tag name
- `description`: Optional description
- `created_at`: Timestamp

### `study_documents`
- `id`: Primary key
- `title`: Document title
- `file_path`: Path to the document file
- `source_info`: Additional information
- `created_at`: Timestamp

### `study_document_tags`
- `document_id`: Foreign key to study_documents
- `tag_id`: Foreign key to study_tags
- Primary key combination prevents duplicate assignments

## API Methods

The following methods are available in the `DatabaseAccess` class:

### Tag Management
- `create_tag(tag_name, description='')`: Creates a new tag
- `get_all_tags()`: Retrieves all available tags
- `get_tags_for_document(document_id)`: Gets tags assigned to a document
- `assign_tag_to_document(document_id, tag_id)`: Assigns a tag to a document
- `remove_tag_from_document(document_id, tag_id)`: Removes a tag from a document

### Document Management
- `get_all_study_documents()`: Retrieves all study documents
- `add_study_document(title, file_path, source_info='')`: Adds a new document

## Example Usage

```python
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

# Initialize database connection
db = DatabaseAccess(**DB_PARAMS)

# Create a new tag
db.create_tag("DelayedCBetOOP", "Delayed continuation bet out of position")

# Get all tags
tags = db.get_all_tags()
for tag_id, tag_name in tags:
    print(f"Tag {tag_id}: {tag_name}")

# Add a document
db.add_study_document("My Study Note", "/path/to/note.md")

# Assign a tag to a document
db.assign_tag_to_document(document_id=1, tag_id=1)

# Get tags for a document
doc_tags = db.get_tags_for_document(1)
for tag_id, tag_name in doc_tags:
    print(f"Document has tag: {tag_name}")

db.close()
```

## Testing

Run the test script to verify tag management functionality:

```bash
python test_tag_management.py
```

This will test:
- Tag creation
- Tag retrieval
- Document creation
- Tag assignment
- Tag removal
- Error handling

## Benefits

1. **Organization**: Categorize study materials by concept or situation
2. **Searchability**: Quickly find documents related to specific topics
3. **Analysis**: Identify patterns in your study materials
4. **Flexibility**: Add or remove tags as your study focus evolves

## Future Enhancements

Potential improvements for the tag management system:
- Tag search and filtering
- Tag-based document queries
- Tag statistics and analytics
- Tag hierarchies and relationships
- Bulk tag operations
- Tag import/export functionality 