from flask import render_template, Response, request
from app import app


def make_error_page(error_type, error_description, code):
    return render_template("error.html", error_type=error_type, error_description=error_description), code


@app.errorhandler(Exception)
def handle_error(e):
    try:
        if e.code < 400:
            return Response.force_type(e, request.environ)
        elif e.code == 401:
            return make_error_page("Não autorizado", "Você não possui autorização para acessar esta página", e.code)
        elif e.code == 404:
            return make_error_page("Não encontrado", "Página não encontrada", e.code)
        raise e
    except:  # if the status code isn't 401 or 404 then is redirected
        if "HX-REQUEST" in request.headers:  #
            response = Response()
            response.headers["hx-redirect"] = "/error"
            return response
        return make_error_page("Erro interno", "Aconteceu um erro inesperado, tente novamente mais tarde.", 500)


@app.route("/error", methods=["GET"])
def error():
    return make_error_page("Erro interno", "Aconteceu um erro inesperado, tente novamente mais tarde.", 500)
