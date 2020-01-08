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


__author__ = "Daniel Lindsley"
__version__ = (1, 0, 0)
__license__ = "New BSD"


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


def generate_problem_and_solution(operations, number_1, number_2):
    op_keys = list(operations.keys())
    operation = random.choice(op_keys)
    problem = "{} {} {}".format(number_1, operation, number_2)
    solution = operations[operation](number_1, number_2)
    return problem, solution


def difficulty_1():
    """
    Simple addition/subtraction.
    """
    operations = {
        "+": addx,
        "-": subx,
    }

    number_1 = random.randint(0, 12)
    number_2 = random.randint(0, 12)

    # Ensure the bigger number is on top, so as not to worry about
    # negative numbers.
    number_1, number_2 = max([number_1, number_2]), min([number_1, number_2])

    return generate_problem_and_solution(operations, number_1, number_2)


def difficulty_2():
    """
    Simple multiplication.
    """
    operations = {
        "*": multx,
    }

    number_1 = random.randint(0, 12)
    number_2 = random.randint(0, 12)
    return generate_problem_and_solution(operations, number_1, number_2)


def difficulty_3():
    """
    Simple division.
    """
    operations = {
        "/": divx,
    }

    # This looks a little backwards, but the point is simple whole number
    # division. No better way than to start with two whole numbers &
    # work backwards...
    number_1 = random.randint(1, 12)
    # Make sure the denominator isn't zero.
    number_2 = random.randint(1, 12)

    solution = number_1 * number_2
    # Now we switch the solution & the numerator.
    number_1 = solution
    return generate_problem_and_solution(operations, number_1, number_2)


def difficulty_4():
    """
    Multi-digit addition.
    """
    operations = {
        "+": addx,
    }

    number_1 = random.randint(10, 300)
    number_2 = random.randint(1, 50)
    return generate_problem_and_solution(operations, number_1, number_2)


def difficulty_5():
    """
    Multi-digit subtraction.
    """
    operations = {
        "-": subx,
    }

    number_1 = random.randint(10, 300)
    number_2 = random.randint(1, 50)

    # Ensure the bigger number is on top, so as not to worry about
    # negative numbers.
    number_1, number_2 = max([number_1, number_2]), min([number_1, number_2])

    return generate_problem_and_solution(operations, number_1, number_2)


def difficulty_6():
    """
    Multi-digit multiplication.
    """
    operations = {
        "*": multx,
    }

    number_1 = random.randint(10, 150)
    number_2 = random.randint(1, 12)
    return generate_problem_and_solution(operations, number_1, number_2)


def difficulty_7():
    """
    Multi-digit division.
    """
    operations = {
        "/": divx,
    }

    # Again, this looks a little backwards, but the point is whole number
    # division. No better way than to start with two whole numbers &
    # work backwards...
    number_1 = random.randint(10, 400)
    # Make sure the denominator isn't zero.
    number_2 = random.randint(1, 20)

    solution = number_1 * number_2
    # Now we switch the solution & the numerator.
    number_1 = solution
    return generate_problem_and_solution(operations, number_1, number_2)


class Problem(peewee.Model):
    problem = peewee.CharField()
    solution = peewee.FloatField(default=0)
    difficulty = peewee.IntegerField(default=1)
    solved_by = peewee.CharField(choices=NAMES)
    started_at = peewee.DateTimeField(default=datetime.datetime.utcnow)
    elapsed = peewee.FloatField(default=0.0)
    attempts = peewee.IntegerField(default=0)

    class Meta:
        database = db

    @classmethod
    def create_new(cls, name, difficulty=1):
        obj = cls(solved_by=name, difficulty=difficulty)
        obj.problem, obj.solution = obj.generate_problem(difficulty)
        obj.save()
        return obj

    def generate_problem(self, difficulty=1):
        if difficulty == 2:
            return difficulty_2()
        elif difficulty == 3:
            return difficulty_3()
        elif difficulty == 4:
            return difficulty_4()
        elif difficulty == 5:
            return difficulty_5()
        elif difficulty == 6:
            return difficulty_6()
        elif difficulty == 7:
            return difficulty_7()

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

    def determine_point_value(self):
        points = 0

        if self.difficulty in (1, 2, 3):
            points = 1
        elif self.difficulty in (4, 5, 6):
            points = 3
        elif self.difficulty in (7,):
            points = 5

        return points


def determine_progress(name, target_points=30):
    today = datetime.date.today()
    problems = Problem.select().where(
        Problem.solved_by == name,
        Problem.started_at >= today,
        Problem.attempts >= 1,
        Problem.elapsed > 0,
    )

    total_points = 0
    percent_complete = 0

    for problem in problems:
        total_points += problem.determine_point_value()

    if total_points != 0:
        percent_complete = int((total_points / target_points) * 100)

    # Clamp it.
    if percent_complete <= 0:
        percent_complete = 0

    if percent_complete >= 100:
        percent_complete = 100

    return {
        "target_points": target_points,
        "total_points": total_points,
        "percent_complete": percent_complete,
    }


def error_404(request, name=None):
    template = env.get_template("404.html")
    context = {"name": name}
    return app.render(request, template.render(context), status_code=404)


@app.get("/")
def index(request):
    template = env.get_template("index.html")
    context = {
        "names": NAMES,
    }
    return app.render(request, template.render(context))


@app.get("/<str:name>/")
def choose_difficulty(request, name):
    if name not in NAMES:
        return error_404(request, name)

    progress = determine_progress(name)

    template = env.get_template("choose_difficulty.html")
    context = {
        "name": name,
        "difficulties": [
            {
                "url": "/{}/difficulty/1/".format(name),
                "name": "Simple Addition/Subtraction",
                "difficulty": "Easy",
                "points": 1,
            },
            {
                "url": "/{}/difficulty/2/".format(name),
                "name": "Multiplication (Times Tables)",
                "difficulty": "Easy",
                "points": 1,
            },
            {
                "url": "/{}/difficulty/3/".format(name),
                "name": "Simple Division",
                "difficulty": "Easy",
                "points": 1,
            },
            {
                "url": "/{}/difficulty/4/".format(name),
                "name": "Bigger Addition",
                "difficulty": "Medium",
                "points": 3,
            },
            {
                "url": "/{}/difficulty/5/".format(name),
                "name": "Bigger Subtraction",
                "difficulty": "Medium",
                "points": 3,
            },
            {
                "url": "/{}/difficulty/6/".format(name),
                "name": "Multiplication",
                "difficulty": "Medium",
                "points": 3,
            },
            {
                "url": "/{}/difficulty/7/".format(name),
                "name": "Division",
                "difficulty": "Hard",
                "points": 5,
            },
        ],
        "progress": progress,
    }
    return app.render(request, template.render(context))


@app.get("/<str:name>/difficulty/<int:difficulty_level>/")
def create_problem(request, name, difficulty_level):
    if name not in NAMES:
        return error_404(request, name)

    problem = Problem.create_new(name, difficulty=difficulty_level)
    uri = "/{}/{}/".format(name, problem.id)
    return app.redirect(request, uri)


@app.post("/<str:name>/<int:problem_id>/")
@app.get("/<str:name>/<int:problem_id>/")
def show_problem(request, name, problem_id):
    if name not in NAMES:
        return error_404(request, name)

    try:
        problem = Problem.get(id=problem_id)
    except Problem.DoesNotExist:
        return error_404(request, name)

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
        return error_404(request, name)

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
    avg_solve_time = 0.0

    for problem in problems:
        if problem.attempts > 0:
            total_solved += 1
            total_attempts += problem.attempts or 0
            total_solve_time += problem.elapsed or 0

    if total_solved != 0:
        avg_solve_time = total_solve_time / total_solved

    progress = determine_progress(name)

    context = {
        "name": name,
        "problems": problems,
        "total_solved": total_solved,
        "total_attempts": total_attempts,
        "avg_solve_time": avg_solve_time,
        "progress": progress,
    }
    template = env.get_template("summary.html")
    return app.render(request, template.render(context))


@app.get("/static/<str:asset_type>/<str:asset_name>")
def static(request, asset_type, asset_name):
    path = os.path.join(PROJECT_ROOT, "static", asset_type, asset_name)
    content_type = itty3.PLAIN

    if not os.path.exists(path):
        return error_404(request)

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
