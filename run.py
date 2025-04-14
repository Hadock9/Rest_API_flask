import uvicorn

if __name__ == "__main__":
    uvicorn.run("library_api.main:app", reload=True)
