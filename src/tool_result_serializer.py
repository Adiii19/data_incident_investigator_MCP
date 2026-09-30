import json

class ToolResultSerializer:

    @staticmethod
    def serialize(result)->str:
         if hasattr(result,"structured_content"):
              structured=result.structured_content

              if structured is not None:
                   return json.dumps(
                        structured,
                        default=str
                   )

         if hasattr(result,"content"):
          texts=[]

          for item in result.content:
              if hasattr(item,"text"):
                  texts.append(item.text)

          if texts:
              return "\n".join(texts)


         return json.dumps(
             result,
             default=str
         )
