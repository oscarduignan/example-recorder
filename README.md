# How to use this tool

The idea is that you configure your browser-based tests to use the proxy started when you run the container. Then after your tests have run you can download a zip of the pages seen during the test run by sending a SHUTDOWN request to the proxy.

To have a play around locally:

1. Build the docker image

    ```
    docker build . -t example-recorder
    ```

2. Run the container to start the proxy

    ```
    docker run --rm -it -p 8080:8080 example-recorder
    ```

3. In another terminal window, open a browser with the proxy

    ```
    chromium --incognito --allow-running-insecure-content --proxy-server="localhost:8080"
    ```

4. Hit a test URL in the browser you just opened, like:

    > http://www.csszengarden.com

5. In another terminal, complete the recording and save the output

    ```
    curl -X SHUTDOWN -x localhost:8080 localhost -o examples.zip
    ```

6. Check the docker container you started in step 2 has now stopped

7. Check examples.zip downloaded in response to the shutdown request you sent contains the page examples

    ```
    unzip -l examples.zip
    ```

8. Profit
