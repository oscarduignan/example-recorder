# How to use this tool

The idea is that you configure your browser-based tests to use the proxy started when you run the container. Then after your tests have run you can download a zip of the pages seen during the test run by sending a SHUTDOWN request to the proxy.

To have a play around locally:

1. Build the docker image

    ```
    docker build . -t example-recorder
    ```

2. Run the container to start the proxy

    ```
    docker run --rm -it -p 8080:8080 \
      -e ZAP_FORWARD_ENABLE=true \
      -e ZAP_FORWARD_PORTS="$(sm -s | grep -E 'PASS|BOOT' | awk '{ print $12}' | tr "\n" " ")" \
      -e HOST_IP="$(ifconfig \
              | grep -m 1 -oE "inet (10\.[0-9]+|172\.(1[6-9]|2[0-9]|3[01])|192\.168)\.[0-9]+\.[0-9]+" \
              | grep -oE "[0-9.]+")" \
    example-recorder
    ```

    > **Note**
    > the ZAP stuff is because when you run the proxy in a container it won't be able to resolve "localhost"
    > so there is rinetd running in the container and it will setup forwarding on each port you list here to
    > the same port on the HOST_IP. There's probably more to it when it comes to running in a ci build where
    > the container the proxy is running in might be in a container cluster.

3. In another terminal window, open a browser with the proxy

    ```
    chromium --incognito --allow-running-insecure-content --proxy-server="localhost:8080" --proxy-bypass-list="<-loopback>"
    ```

    > **Note**
    > If you omit the proxy bypass config then localhost requests won't go through the proxy (but also won't 
    > fail). If you include it and you haven't forwarded the ports using `ZAP_FORWARD_PORTS` then those
    > requests will fail with a 502 bad gateway.

4. Hit a test URL in the browser you just opened, like:

    > http://www.csszengarden.com

5. In another terminal, complete the recording and save the output

    ```
    curl -X SHUTDOWN -x localhost:8080 localhost -o recorded-examples.zip
    ```

6. Check the docker container you started in step 2 has now stopped

7. Check examples.zip downloaded in response to the shutdown request you sent contains the page examples

    ```
    unzip -l recorded-examples.zip
    unzip recorded-examples -d ./recorded-examples
    chromium ./recorded-examples
    ```

8. Profit
