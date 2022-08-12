#!/bin/bash
# build package

# lint and validate
function validate {

    if [[ $1 ]]; then
        check_path="$1"
    else
        check_path="."
    fi

    echo "run validate on $check_path"
    
    echo "running bandit"
    bandit --recursive --skip B105,B108,B404,B603,B607 "$check_path"
    echo "running black"
    black --diff --color --check -l 79 "$check_path"
    echo "running codespell"
    codespell --skip="./.git" "$check_path"
    echo "running flake8"
    flake8 "$check_path" --count --max-complexity=12 --max-line-length=79 \
        --show-source --statistics
    echo "running isort"
    isort --check-only --diff --profile black -l 79 "$check_path"
    printf "    \n> all validations passed\n"

}

function localbuild {
    echo "install local build"
    pip uninstall -y ryd-client
    python -m build
    pip install . --user
}

function publish {
    echo "publish new release"
    printf "\ncreate new version:\n"
    read -r VERSION
    echo "$VERSION"

    git push
    find dist/ -type f ! -name "*$VERSION*" -exec trash {} \;
    python -m build
    twine upload dist/*
    git tag -a "$VERSION" -m "new release version $VERSION"
    git push "$VERSION"
}

if [[ $1 == "publish" ]]; then
    publish "$2"
elif [[ $1 == "localbuild" ]]; then
    localbuild
elif [[ $1 == "validate" ]]; then
    validate "$2"
else
    echo "valid options are: publish | localbuild | validate"
fi

##
exit 0
