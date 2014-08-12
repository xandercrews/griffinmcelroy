building
--------
building postgres:

    pushd postgres;
    docker build --rm -t griffinmcelroy/postgres .
    popd

build the standalone gatherer and install griffinmcelroy:

    pushd standalone;
    docker build --rm -t griffinmcelroy/standalone-preinstall .
    popd
    docker run -t -i -v $(readlink -e python)/:/src/ griffinmcelroy/standalone-preinstall sh /bin/griffin-develop.sh
    docker commit <container id> griffinmcelroy/standalone
    
running and linking
-------------------

    docker run -P -d --name=demosnmpagent griffinmcelroy/demosnmpagent
    docker run -P -d --name=postgres griffinmcelroy/postgres
    docker run -t -i -v $(readlink -e python)/:/src/ --link postgres:db --link demosnmp:demosnmp griffinmcelroy/standalone bash
