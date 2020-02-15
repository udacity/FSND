# Recipes

## Projects

### Fyyur

#### Flask-SQLAlchemy: check if row exists in table

```python
exists = db.session.query(User.id).filter_by(name='davidism').scalar() is not None
```

##### References
* https://stackoverflow.com/a/32952421/4107440
* https://stackoverflow.com/a/40919686/4107440


#### Bootstrap: showing alerts

Example of use:

```html
<div class="alert alert-primary" role="alert">
  This is a primary alert—check it out!
</div>
<div class="alert alert-secondary" role="alert">
  This is a secondary alert—check it out!
</div>
<div class="alert alert-success" role="alert">
  This is a success alert—check it out!
</div>
<div class="alert alert-danger" role="alert">
  This is a danger alert—check it out!
</div>
<div class="alert alert-warning" role="alert">
  This is a warning alert—check it out!
</div>
<div class="alert alert-info" role="alert">
  This is a info alert—check it out!
</div>
<div class="alert alert-light" role="alert">
  This is a light alert—check it out!
</div>
<div class="alert alert-dark" role="alert">
  This is a dark alert—check it out!
</div>
```

##### References
* https://getbootstrap.com/docs/4.0/components/alerts/

#### Flask: Message Flashing with categories

Example of usage:

```python
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    <ul class=flashes>
    {% for category, message in messages %}
      <li class="{{ category }}">{{ message }}</li>
    {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
```

##### References
* https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/

#### Flask: CSRF Protection

Example of usage:

```python
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
```

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

```python
<form method="post">
    {{ form.csrf_token }}
</form>
```

##### References
* https://flask-wtf.readthedocs.io/en/stable/quickstart.html#creating-forms
* https://flask-wtf.readthedocs.io/en/stable/csrf.html
* https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask

#### Flask Migrate: migration for String length change

Edit run_migrations_offline() method:

```python
context.configure(
    url=url, target_metadata=target_metadata, literal_binds=True,
    compare_type=True
)
```

Edit run_migrations_online() method:

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True
)
```
##### References
* https://eshlox.net/2017/08/06/alembic-migration-for-string-length-change

##### Resources
* [Project Instructions](https://classroom.udacity.com/nanodegrees/nd0044/parts/216c669c-5e62-43a1-bcb9-8a8e5eca972a/modules/43f34772-8032-4851-938b-d952bbfc7f1c/lessons/af04d96a-6182-43a0-af07-157d1bd389d0/concepts/7107ad1d-63ca-4cb8-a9ae-bb3ffc1847b8)
* [Rubric](https://review.udacity.com/#!/rubrics/2653/view)
* [Project](https://classroom.udacity.com/nanodegrees/nd0044/parts/216c669c-5e62-43a1-bcb9-8a8e5eca972a/modules/43f34772-8032-4851-938b-d952bbfc7f1c/lessons/af04d96a-6182-43a0-af07-157d1bd389d0/project)
