document.addEventListener("DOMContentLoaded", function() {
    fetchTasks();
});

function fetchTasks() {
    fetch("/tasks")
        .then(response => response.json())
        .then(tasks => {
            const taskList = document.getElementById("task-list");
            taskList.innerHTML = "";
            tasks.forEach(task => {
                const taskItem = document.createElement("li");
                taskItem.innerHTML = `
                    <input type="checkbox" ${task.completed ? 'checked' : ''} onchange="toggleComplete('${task.title}', this.checked)">
                    <span class="${task.completed ? 'completed' : ''}">${task.title}</span>
                    <div class="actions">
                        <i class="fas fa-edit" onclick="editTask('${task.title}')"></i>
                        <i class="fas fa-trash" onclick="deleteTask('${task.title}')"></i>
                    </div>
                `;
                taskList.appendChild(taskItem);
            });
        });
}

function toggleComplete(title, completed) {
    fetch(`/tasks/${title}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ completed: completed })
    }).then(response => {
        if (response.ok) {
            fetchTasks();
        }
    });
}
function addTask() {
    const taskInput = document.getElementById("task-input");
    const taskTitle = taskInput.value;
    if (taskTitle) {
        fetch("/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ title: taskTitle, completed: false })
        }).then(response => {
            if (response.ok) {
                taskInput.value = "";
                fetchTasks();
            }
        });
    }
}

function editTask(title) {
    const newTitle = prompt("Edit task title:", title);
    if (newTitle) {
        fetch(`/tasks/${title}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ title: newTitle })
        }).then(response => {
            if (response.ok) {
                fetchTasks();
            }
        });
    }
}

function deleteTask(title) {
    fetch(`/tasks/${title}`, {
        method: "DELETE"
    }).then(response => {
        if (response.ok) {
            fetchTasks();
        }
    });
}