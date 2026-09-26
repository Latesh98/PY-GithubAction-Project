const form = document.getElementById("task-form");
const input = document.getElementById("task-input");
const list = document.getElementById("task-list");

// GET /api/tasks -> load and draw all tasks
async function loadTasks() {
    const res = await fetch("/api/tasks");
    const tasks = await res.json();
    list.innerHTML = "";
    tasks.forEach(renderTask);
}

function renderTask(task) {
    const li = document.createElement("li");
    li.className = task.done ? "done" : "";

    const span = document.createElement("span");
    span.textContent = task.text;
    span.onclick = () => toggleTask(task.id);

    const delBtn = document.createElement("button");
    delBtn.textContent = "✕";
    delBtn.className = "delete-btn";
    delBtn.type = "button";
    delBtn.onclick = () => deleteTask(task.id);

    li.appendChild(span);
    li.appendChild(delBtn);
    list.appendChild(li);
}

// POST /api/tasks -> create a new task
async function addTask(text) {
    const res = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });
    if (!res.ok) {
        const err = await res.json();
        alert(err.error);
        return;
    }
    loadTasks();
}

// PATCH /api/tasks/<id> -> flip done/not-done
async function toggleTask(id) {
    await fetch(`/api/tasks/${id}`, { method: "PATCH" });
    loadTasks();
}

// DELETE /api/tasks/<id> -> remove a task
async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, { method: "DELETE" });
    loadTasks();
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (text) {
        addTask(text);
        input.value = "";
    }
});

// "Show All Tasks" button -> just re-fetches everything from the backend
document.getElementById("show-all-btn").addEventListener("click", loadTasks);

loadTasks();
