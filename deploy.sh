#!/bin/bash

# Configuration
FUNCTION_NAME="zuna-grey-bbs"
ZIP_FILE="deployment_package.zip"

echo "--- Zuna Grey AWS Deployment ---"

# 1. Check if AWS CLI is installed
if ! command -v aws &> /dev/null
then
    echo "ERROR: AWS CLI not found. Please install it to continue."
    exit 1
fi

# 2. Package the code
echo "Packaging code..."
# Remove old zip if exists
rm -f $ZIP_FILE
# Zip only necessary files (handler and html)
zip -r $ZIP_FILE lambda_function.py index.html
echo "Package created: $ZIP_FILE"

# 3. Check if function exists
echo "Checking for existing function '$FUNCTION_NAME'..."
if aws lambda get-function --function-name "$FUNCTION_NAME" >/dev/null 2>&1; then
    echo "Function exists. Updating code..."
    aws lambda update-function-code \
        --function-name "$FUNCTION_NAME" \
        --zip-file "fileb://$ZIP_FILE"
    echo "Update complete."
else
    echo "Function does not exist. Creating new function '$FUNCTION_NAME'..."
    # Warning: This assumes a default execution role exists or needs to he specfied. 
    # For simplicity in this script, we'll try to create it, but often roles are complex to guess.
    # A better approach for a "hosted" request is to create the zipped package and ask the user to just upload it if they aren't IAM experts,
    # OR try to create with a basic role if we knew one.
    
    echo "!! ERROR: Creating a NEW function via CLI requires an IAM Role ARN."
    echo "!! Please create the function manually in AWS Console named '$FUNCTION_NAME' with Python 3.x runtime,"
    echo "!! OR provide an IAM Role ARN to this script."
    echo " "
    echo "Package $ZIP_FILE is ready for manual upload in the AWS Console."
    exit 1
fi

# 4. Cleanup
# rm $ZIP_FILE
echo "Done."
