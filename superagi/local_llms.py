from superagi.config.config import get_config
from superagi.lib.logger import logger

OOBA_PROVIDER = "ooba-booga"


def install_local_llms(session):
    if get_config("ENV", "PROD") != "DEV":
        return

    logger.info("Installing local LLMs, if needed")
    from superagi.models.models import Models
    from superagi.models.models_config import ModelsConfig

    organisation_id = 1

    # Add the model providers if needed
    model_providers = (
        session.query(ModelsConfig)
        .filter(ModelsConfig.org_id == organisation_id)
        .filter(ModelsConfig.provider == OOBA_PROVIDER)
        .all()
    )

    if model_providers:
        logger.info("Ooba-Booga provider already exists")
        ooba_provider = model_providers[0]
    else:
        ooba_provider = ModelsConfig(org_id=organisation_id, provider=OOBA_PROVIDER, api_key="")
        session.add(ooba_provider)
        session.commit()
        # session.flush()  # not needed?
        session.refresh(ooba_provider)
        logger.info(f"Created Ooba-Booga provider as {ooba_provider.id}")

    existing = Models.fetch_models(session, 1)
    local_models = {
        OOBA_PROVIDER: {
            "name": OOBA_PROVIDER,
            "description": "Local models using the Text Generation Web UI",
            "end_point": "uses_environment_variable",
            "model_provider_id": ooba_provider.id,
            "token_limit": 4096,  # ignored
            "type": "local LLM",
            "version": 1,
        }
    }
    models_to_add = set(local_models.keys())
    for model in existing:
        if model["name"] in models_to_add:
            models_to_add.remove(model["name"])
    for model_name in models_to_add:
        logger.info(f"Creating local model {model_name}")
        model_info = local_models[model_name]
        result = Models.store_model_details(
            session,
            organisation_id,
            model_info["name"],
            model_info["description"],
            model_info["end_point"],
            model_info["model_provider_id"],
            model_info["token_limit"],
            model_info["type"],
            model_info["version"],
        )
        logger.info(f"Store local model {model_name} result: {result}")
