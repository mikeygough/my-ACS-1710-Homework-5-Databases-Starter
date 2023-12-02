from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################


@app.route("/")
def plants_list():
    """Display the plants list page."""

    # retrieve *all* plants from the `plants` collection.
    plants_data = mongo.db.plants.find()
    plants_data = list(plants_data)

    context = {
        "plants": plants_data,
    }
    return render_template("plants_list.html", **context)


@app.route("/about")
def about():
    """Display the about page."""
    return render_template("about.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == "POST":
        # Get the new plant's name, variety, photo, & date planted, and
        # store them in the object below.
        name = request.form["plant_name"]
        variety = request.form["variety"]
        photo_url = request.form["photo"]
        date_planted = request.form["date_planted"]
        new_plant = {
            "name": name,
            "variety": variety,
            "photo_url": photo_url,
            "date_planted": date_planted,
        }

        # Insert the object into the `plants` collection
        # Pass the inserted id into the redirect call below.
        result = mongo.db.plants.insert_one(new_plant)
        result_id = result.inserted_id
        return redirect(url_for("detail", plant_id=f"{result_id}"))

    else:
        return render_template("create.html")


@app.route("/plant/<plant_id>")
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    # retrieve *one* plant from the database, whose id matches the id passed in via the URL.
    # check for valid objectID
    try:
        plant_to_show = mongo.db.plants.find_one({"_id": ObjectId(plant_id)})
    except:
        return render_template("error.html")
    
    # check for valid db return
    if plant_to_show == None:
        return render_template("error.html")
    
    # find all harvests for the plant's id.
    harvests = mongo.db.harvests.find({"plant_id": plant_id})
    harvests = list(harvests)

    context = {"plant": plant_to_show, "harvests": harvests}
    return render_template("detail.html", **context)


@app.route("/harvest/<plant_id>", methods=["POST"])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    # Create a new harvest object
    quantity = request.form["harvested_amount"]
    date = request.form["date_planted"]

    new_harvest = {
        "quantity": quantity,  # e.g. '3 tomatoes'
        "date": date,
        "plant_id": plant_id,
    }

    # insert the object into the `harvests` collection of the database
    result = mongo.db.harvests.insert_one(new_harvest)
    return redirect(url_for("detail", plant_id=plant_id))


@app.route("/edit/<plant_id>", methods=["GET", "POST"])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == "POST":
        # set search params
        searchParam = {"_id": ObjectId(plant_id)}

        # get new values
        name = request.form["plant_name"]
        variety = request.form["variety"]
        photo_url = request.form["photo"]
        date_planted = request.form["date_planted"]
        updated_plant = {
            "name": name,
            "variety": variety,
            "photo_url": photo_url,
            "date_planted": date_planted,
        }
        # set changes
        changes = {"$set": updated_plant}
        # update the plant
        updated_plant = mongo.db.plants.update_one(searchParam, changes)
        return redirect(url_for("detail", plant_id=plant_id))
    else:
        # get the plant object with the passed-in _id.
        # check for valid objectID
        try:
            plant_to_show = mongo.db.plants.find_one({"_id": ObjectId(plant_id)})
        except:
            return render_template("error.html")
        
        # check for valid db return
        if plant_to_show == None:
            return render_template("error.html")

        context = {"plant": plant_to_show}
        return render_template("edit.html", **context)


@app.route("/delete/<plant_id>", methods=["POST"])
def delete(plant_id):
    # delete the plant with the given id
    result = mongo.db.plants.delete_one({"_id": ObjectId(plant_id)})
    print("delete success?", result.deleted_count)

    result = mongo.db.harvests.delete_many({"plant_id": plant_id})
    print("deletes success?", result.deleted_count)
    
    return redirect(url_for("plants_list"))

if __name__ == "__main__":
    app.run(debug=True)
