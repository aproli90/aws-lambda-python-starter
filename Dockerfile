FROM public.ecr.aws/lambda/python:3.12

# Copy the entire project to the Lambda task root
COPY . ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Create an empty __init__.py file in the src directory to make it a proper package
RUN touch ${LAMBDA_TASK_ROOT}/src/__init__.py

# Add the Lambda task root to PYTHONPATH to enable absolute imports
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}"
