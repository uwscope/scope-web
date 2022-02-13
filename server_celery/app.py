import celery

app = celery.Celery("celery")
app.conf.update(
    {
        "broker_url": "filesystem://localhost//",
        "broker_transport_options": {
            "data_folder_in": "./broker/data",
            "data_folder_out": "./broker/data",
            "data_folder_processed": "./broker/processed",
        },
    }
)

if __name__ == "__main__":
    app.start()
