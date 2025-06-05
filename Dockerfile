FROM public.ecr.aws/lambda/python:3.12

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Upgrade pip and install dependencies to a separate location to avoid conflicts
RUN pip install --upgrade pip
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt \
    --target "${LAMBDA_TASK_ROOT}/lib" \
    --no-cache-dir

# Copy the entire project to the Lambda task root
COPY . ${LAMBDA_TASK_ROOT}/

# Create an empty __init__.py file in the src directory to make it a proper package
RUN touch ${LAMBDA_TASK_ROOT}/src/__init__.py

# Add both the Lambda task root and lib directory to PYTHONPATH
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}:${LAMBDA_TASK_ROOT}/lib"
