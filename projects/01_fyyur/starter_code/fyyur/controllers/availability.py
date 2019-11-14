import sys
from fyyur import app, db
from fyyur.forms import *
from flask import jsonify
from fyyur.models.availability import Availability
from fyyur.models.artist import Artist
from flask import Flask, render_template, request, Response, flash, redirect, url_for


@app.route('/availability/<int:artist_id>', methods=['GET'])
def availability(artist_id):

    availability = Availability.query.filter_by(artist_id=artist_id).all()
    artist = Artist.query.with_entities(Artist.name).filter_by(id=artist_id).first()
    form = AvailabilityForm()

    data = {
        'artist_id': artist_id,
        'artist_name': artist.name,
        'availability': []
    }

    for slot in availability:
        data['availability'].append(
            {
                'id': slot.id,
                'to_time': str(slot.to_time),
                'from_time': str(slot.from_time),
            }
        )

    return render_template('pages/availability.html', data=data, form=form)


@app.route('/availability/<int:artist_id>', methods=['POST'])
def add_availability(artist_id):
    from_time = request.form.get('from_time', '')
    to_time = request.form.get('to_time', '')

    artist_availability = Availability(
        from_time=from_time, to_time=to_time, artist_id=artist_id)

    error = False

    try:
        db.session.add(artist_availability)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        return redirect(url_for('availability', artist_id=artist_id))
    else:
        return jsonify({
            'status': 400,
            'message': 'availability addition failed'
        })


@app.route('/availability/<int:artist_id>/edit', methods=['POST'])
def edit_availability(artist_id):
    id = request.json.get('availability_id', '')
    from_time = request.json.get('from_time', '')
    to_time = request.json.get('to_time', '')

    availability = Availability.query.filter(id=id, artist_id=artist_id)

    availability.from_time = from_time
    availability.to_time = to_time

    error = False

    try:
        db.session.add(availability)
        db.session.commit()
    except:
        fb.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        return jsonify({
            'status': 200,
            'message': 'availability updated'
        })
    else:
        return jsonify({
            'status': 400,
            'message': 'availability update failed'
        })

@app.route('/availability/<int:artist_id>/<int:availability_id>', methods=['DELETE'])
def delete_availability(artist_id, availability_id):
    slot = Availability.query.get(availability_id)

    error = False
    try:
        db.session.delete(slot)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    print(artist_id)
    if not error:
        return jsonify({
            'status': 200,
            'message': 'Slot deleted succesfuly'
        })
    else:
         return jsonify({
            'status': 400,
            'message': 'Slot delete failed'
        })
