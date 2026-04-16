import typer
import httpx

app = typer.Typer(help='authwall CLI')


@app.command()
def sessions(base_url: str = 'http://localhost:8000') -> None:
    r = httpx.get(f'{base_url}/api/v1/sessions', timeout=5)
    typer.echo(r.text)


@app.command()
def force_offline(session_id: str, token: str, base_url: str = 'http://localhost:8000') -> None:
    headers = {'Authorization': f'Bearer {token}'}
    r = httpx.delete(f'{base_url}/api/v1/sessions/{session_id}', headers=headers, timeout=5)
    typer.echo(r.text)


if __name__ == '__main__':
    app()
