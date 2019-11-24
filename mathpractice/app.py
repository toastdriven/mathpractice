"""

Setup:

    >>> import app
    >>> app.create_tables([app.Problem])

"""
import datetime
import os
import random

import itty3
import jinja2
import peewee


app = itty3.App(debug=bool(os.environ.get("APP_DEBUG", 0)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
NAMES = os.environ.get("APP_NAMES", "").split(",")

db = peewee.SqliteDatabase("results.db")
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("./templates", followlinks=True),
    autoescape=jinja2.select_autoescape(["html"]),
)


def addx(*args):
    return sum(args)


def subx(*args):
    current = args[0]

    for val in args[1:]:
        current -= val

    return current


def multx(*args):
    current = args[0]

    for val in args[1:]:
        current *= val

    return current


def divx(*args):
    current = args[0]

    for val in args[1:]:
        current /= val

    return current


def difficulty_1():
    operations = {
        "+": addx,
        "-": subx,
    }

    number_1 = random.randint(0, 12)
    number_2 = random.randint(0, 12)

    op_keys = list(operations.keys())
    operation = random.choice(op_keys)
    problem = "{} {} {}".format(number_1, operation, number_2)
    solution = operations[operation](number_1, number_2)
    return problem, solution


def difficulty_2():
    operations = {
        "*": multx,
    }

    number_1 = random.randint(0, 12)
    number_2 = random.randint(0, 12)

    op_keys = list(operations.keys())
    operation = random.choice(op_keys)
    problem = "{} {} {}".format(number_1, operation, number_2)
    solution = operations[operation](number_1, number_2)
    return problem, solution


def difficulty_3():
    operations = {
        "/": divx,
    }

    number_1 = random.randint(10, 100)
    number_2 = random.randint(0, 12)

    # Make sure the denominator isn't zero.
    while number_2 == 0:
        number_2 = random.randint(0, 12)

    # Make sure the bigger number is on top for this difficulty.
    number_1, number_2 = max([number_1, number_2]), min([number_1, number_2])

    op_keys = list(operations.keys())
    operation = random.choice(op_keys)
    problem = "{} {} {}".format(number_1, operation, number_2)
    solution = operations[operation](number_1, number_2)
    return problem, solution


class Problem(peewee.Model):
    problem = peewee.CharField()
    solution = peewee.FloatField(default=0)
    solved_by = peewee.CharField(choices=NAMES)
    started_at = peewee.DateTimeField(default=datetime.datetime.utcnow)
    elapsed = peewee.FloatField(default=0.0)
    attempts = peewee.IntegerField(default=0)

    class Meta:
        database = db

    @classmethod
    def create_new(cls, name, difficulty=1):
        obj = cls(solved_by=name)
        obj.problem, obj.solution = obj.generate_problem(difficulty)
        obj.save()
        return obj

    def generate_problem(self, difficulty=1):
        if difficulty == 2:
            return difficulty_2()
        elif difficulty == 3:
            return difficulty_3()

        return difficulty_1()

    def add_attempt(self, answer):
        self.attempts += 1
        answered = False

        converted_answer = "{:0.3f}".format(answer)
        converted_solution = "{:0.3f}".format(self.solution)

        if converted_answer == converted_solution:
            self.mark_correct()
            answered = True

        self.save()
        return answered

    def mark_correct(self):
        time_taken = datetime.datetime.utcnow() - self.started_at
        self.elapsed = time_taken.total_seconds()


@app.get("/")
def index(request):
    template = env.get_template("index.html")
    context = {
        "names": NAMES,
    }
    return app.render(request, template.render(context))


@app.get("/<str:name>/")
def choose_difficulty(request, name):
    template = env.get_template("choose_difficulty.html")
    context = {
        "name": name,
        "difficulties": [
            {
                "url": "/{}/difficulty/1/".format(name),
                "name": "Addition/Subtraction",
                "difficulty": "Easy",
            },
            {
                "url": "/{}/difficulty/2/".format(name),
                "name": "Multiplication (Times Tables)",
                "difficulty": "Easy",
            },
            {
                "url": "/{}/difficulty/3/".format(name),
                "name": "Division",
                "difficulty": "Medium",
            },
        ],
    }
    return app.render(request, template.render(context))


@app.get("/<str:name>/difficulty/<int:difficulty_level>/")
def create_problem(request, name, difficulty_level):
    if name not in NAMES:
        return app.error_404()

    problem = Problem.create_new(name, difficulty=difficulty_level)
    uri = "/{}/{}/".format(name, problem.id)
    return app.redirect(request, uri)


@app.post("/<str:name>/<int:problem_id>/")
@app.get("/<str:name>/<int:problem_id>/")
def show_problem(request, name, problem_id):
    if name not in NAMES:
        return app.error_404()

    try:
        problem = Problem.get(id=problem_id)
    except Problem.DoesNotExist:
        return app.error_404()

    if request.method == itty3.POST:
        answer = float(request.POST.get("answer", "-1"))

        if problem.add_attempt(answer):
            return app.render_json(
                request,
                {"success": True, "redirect_to": "/{}/".format(name),},
            )

        return app.render_json(request, {"success": False})

    template = env.get_template("problem.html")
    context = {
        "problem": problem,
        "name": name,
    }
    return app.render(request, template.render(context))


@app.get("/<str:name>/summary/")
def show_todays_summary(request, name):
    if name not in NAMES:
        return app.error_404()

    today = datetime.date.today()
    problems = (
        Problem.select()
        .where(Problem.solved_by == name, Problem.started_at >= today)
        .order_by("started_at")
    )

    # STATS!
    total_solved = 0
    total_attempts = 0
    total_solve_time = 0.0

    for problem in problems:
        total_solved += 1
        total_attempts += problem.attempts or 0
        total_solve_time += problem.elapsed or 0

    avg_solve_time = total_solve_time / total_solved

    context = {
        "name": name,
        "problems": problems,
        "total_solved": total_solved,
        "total_attempts": total_attempts,
        "avg_solve_time": avg_solve_time,
    }
    template = env.get_template("summary.html")
    return app.render(request, template.render(context))


@app.get("/static/<str:asset_type>/<str:asset_name>")
def static(request, asset_type, asset_name):
    path = os.path.join(PROJECT_ROOT, "static", asset_type, asset_name)
    content_type = itty3.PLAIN

    if not os.path.exists(path):
        return app.error_404()

    if asset_type == "js":
        content_type = "application/javascript"
    elif asset_type == "img":
        content_type = "image/png"
    elif asset_type == "css":
        content_type = "text/css"

    with open(path, "rb") as raw_file:
        content = raw_file.read()

    return app.render(
        request, content.decode("utf-8"), content_type=content_type
    )


if __name__ == "__main__":
    app.run()
