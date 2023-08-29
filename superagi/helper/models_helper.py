from superagi.llms.hugging_face import HuggingFace

class ModelsHelper:
    @staticmethod
    def validate_end_point(model_api_key, end_point, model_provider):
        response = {"success": True}

        if (model_provider == 'Hugging Face'):
            try:
                result = HuggingFace(api_key=model_api_key, end_point=end_point).verify_end_point()
            except Exception as e:
                response['success'] = False
                response['error'] = str(e)
            else:
                response['result'] = result

        return response


