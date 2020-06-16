
var checkboxes = document.querySelectorAll('.check-completed');
for (let i = 0; i < checkboxes.length; i++) {
  const checkbox = checkboxes[i];
  checkbox.addEventListener("change", sendCompletedTodo)
}


document.getElementById('newTodoForm').onsubmit = function(event) {
  event.preventDefault();
  console.log("event", event);
  fetch('/api/todo/create', {
    method: 'POST',
    body: JSON.stringify(
    {
      'description': document.getElementById('description').value,
      'list_id': event.target.dataset['id']
    }),
    headers:
    {
      'Content-Type': 'application/json'
    }
  }).then( function(response) { return response.json()
  }).then( function(jsonResponse) { renderTodo(jsonResponse)
  }).catch( function(e) {
    console.log(e);
    document.getElementById('error-message').className = '';
  })
}


document.getElementById('newListForm').onsubmit = function(event) {
  event.preventDefault();
  console.log("event", event);
  fetch('api/todolist/create', {
      method: 'POST',
      body: JSON.stringify({
        'name': document.getElementById('name').value,
      }),
      headers: {
        'Content-Type': 'application/json'
      }
  }).then( function(response) { return response.json()
  }).then( function(jsonResponse) {
    const liItem = document.createElement('LI');
    const newTodoList = document.createElement('input');
    const newTodoListDelete = document.createElement('input');
    console.log('jsonResponse', jsonResponse);

    newTodoList.setAttribute('type', 'button');
    newTodoList.setAttribute('value', jsonResponse['name']);
    newTodoList.setAttribute('data-id', jsonResponse['id']);
    newTodoList.addEventListener('click', getTodoList);

    newTodoListDelete.setAttribute('type', 'button');
    newTodoListDelete.setAttribute('value', 'Delete');
    newTodoListDelete.setAttribute('data-id', jsonResponse['id']);
    newTodoListDelete.addEventListener('click', deleteTodoList);

    liItem.setAttribute('data-id', jsonResponse['id']);
    liItem.appendChild(newTodoList);
    liItem.append(" ");
    liItem.appendChild(newTodoListDelete);

    document.getElementById('todolists').appendChild(liItem);
  }).catch( function(e) {
    console.log(e);
    document.getElementById('error-message').className = '';
  })
}


function deleteTodoList(event) {
  console.log('event', event)
}


function getTodoList(event) {
  console.log('event', event);
  listId = event.target.dataset['id'];
  fetch('/api/todolist', {
    method: 'POST',
    body: JSON.stringify(
        {
            'id': listId
        }
    ),
    headers: {
        'Content-Type': 'application/json'
    }
  }).then( function (response) {
    return response.json()
  }).then( function(jsonResponse) {
    console.log(jsonResponse);
    const listNameHeader = document.getElementById('list_name');
    const newTodoForm = document.getElementById('newTodoForm');
    const listOfTodos = document.getElementById('todos');
    const todoList = jsonResponse['todolist'];
    const todos = todoList['todos'];

    // 1) update listNameHeader's Text
    console.log("listNameHeader", listNameHeader);
    listNameHeader.innerHTML = todoList['name'];

    // 2) update newTodoForm id
    newTodoForm.setAttribute("data-id", todoList['id']);

    // 3) Empty list of todos
    while(listOfTodos.firstChild && listOfTodos.removeChild(listOfTodos.firstChild));
    console.log('emptyTodos', listOfTodos);

    // 4) Fill list of todos
    console.log('todos', listOfTodos);
    for (let i = 0; i < todos.length; i++) {
        renderTodo(todos[i])
    }
  })
  .catch( function(e) {
    console.log(e);
    document.getElementById('error-message').className = '';
  })
}


function sendDeleteTodo(event) {
  console.log('event', event );
  const todoId = event.target.dataset['id'];
  fetch('/api/todo/delete', {
    method: 'POST',
    body: JSON.stringify(
        {
            'id': todoId
        }
    ),
    headers: {
        'Content-Type': 'application/json'
    }
  }).then(function(response) { return response.json()
  }).then(function(jsonResponse) {
    liElement = event.target.parentElement
    console.log(jsonResponse);
    console.log('parent', liElement);
    liElement.parentNode.removeChild(liElement)
  })
  .catch( function(e) {
    console.log(e);
    document.getElementById('error-message').className = '';
  })
}


function sendCompletedTodo(event) {
  console.log('event', event );
  newCompleted = event.target.checked;
  checkboxId = event.target.dataset['id'];
  fetch('/api/todo/completed', {
    method: 'POST',
    body: JSON.stringify(
      {
      'completed': newCompleted,
      'id': checkboxId
      }
    ),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(function(response) { return response.json()
  }).then(function(jsonResponse) { console.log(jsonResponse);
  }).catch( function(e) {
    console.log(e);
    document.getElementById('error-message').className = '';
  })
}


function renderTodo(jsonResponse) {
  console.log('renderTodo', jsonResponse);
  const liItem = document.createElement('LI');
  const newCheckbox = document.createElement('input');
  const newDelete = document.createElement('input');

  newCheckbox.className = "check-completed";
  newCheckbox.setAttribute("type", "checkbox");
  newCheckbox.setAttribute("data-id", jsonResponse['id']);
  newCheckbox.checked = jsonResponse['completed'];
  console.log(newCheckbox);

  newDelete.setAttribute("type", "button");
  newDelete.setAttribute("value", "Delete");
  newDelete.setAttribute("data-id", jsonResponse['id']);
  console.log(newDelete);

  liItem.appendChild(newCheckbox);
  liItem.append(jsonResponse['description']);
  liItem.appendChild(newDelete);

  document.getElementById('todos').appendChild(liItem);
  newCheckbox.addEventListener("change", sendCompletedTodo)
  newDelete.addEventListener("click", sendDeleteTodo)

  document.getElementById('error-message').className = 'hidden';
}

