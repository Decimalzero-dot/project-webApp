from django.contrib import admin
from .models import TaskCategory, Task
# Register your models here.

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    # Display the name and icon class in the list view
    list_display = ('name', 'icon_class', 'task_count') 
    # Enable searching by category name
    search_fields = ('name',) 
    
    # Add a method to display the count of tasks in each category (optional, but useful)
    def task_count(self, obj):
        return obj.tasks.count()
    
    task_count.short_description = 'No. of Tasks'

# If you have a basic Task model, register it here too:
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'freelancer', 'client', 'category', 'status', 'budget')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at' # Assumes your Task model has a 'created_at' field