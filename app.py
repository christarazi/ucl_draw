from flask import Flask, render_template, redirect, \
    url_for, request, flash, escape

import os, time
import simulator # Import simulator code

app = Flask(__name__)

app.secret_key = os.urandom(24)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Number of simulations
            n = int(escape(request.form["simulations"]))

            if n > 1000000:
                flash("Error: 1,000,000 is the maximum number of simulations.")
            elif n < 1:
                flash("Error: Number must be greater than zero.")
            else:
                start = time.perf_counter()
                draws, gw, gr = simulator.execute_simulation(n)
                end = time.perf_counter()
                return render_template("results.html", draws=draws, n=n, time=end - start,
                                       winners=gw, runners_up=gr)
        except Exception as e:
            print(e)
            flash("Error: Tricky tricky, only numbers are accepted here.")
    # else:

    return render_template("form.html")


@app.context_processor
def utility_processor():
    def format_odds(odds):
        # Format floating point to 5 decimal places.
        return "{0:.5}".format(odds)

    return dict(format_odds=format_odds)


if __name__ == "__main__":
    app.run()
