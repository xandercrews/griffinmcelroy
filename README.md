building
--------
you only have to build one or the other storage backend unless you want to try both.  in that case you can remove the --link directives when the service starts

building postgres:

    pushd docker/postgres;
    docker build --rm -t griffinmcelroy/postgres .
    popd
    
building hadoop (takes a while- upstream image has hundreds of layers?):

    pushd docker/hadoop;
    docker build --rm -t griffinmcelroy/hadoop .
    popd

build the standalone gatherer and install griffinmcelroy:

    pushd docker/standalone;
    docker build --rm -t griffinmcelroy/standalone-preinstall .
    popd
    docker run -t -i -v $(readlink -e python)/:/src/ griffinmcelroy/standalone-preinstall sh /bin/griffin-develop.sh
    docker commit <container id> griffinmcelroy/standalone
    
running and linking
-------------------

    docker run -P -d --name=demosnmpagent griffinmcelroy/demosnmpagent
    docker run -P -d --name=postgres griffinmcelroy/postgres
    docker run -P -d --name=hadoop griffinmcelroy/hadoop
    docker run -t -i -v $(readlink -e python)/:/src/ --link postgres:db --link demosnmpagent:snmp --link hadoop:hadoop griffinmcelroy/standalone bash
    (from in the griffin standalone container)
    vim /conf/griffin-standalone.conf
    python2.7 /src/bin/gatherer_standalone.py -c /conf/griffin-standalone.conf
    
you can edit /conf/griffin-standalone.conf to switch storage backends from postgres to hadoop
if it succeeded in starting it should look something like this

    root@e8eee0c82ab5:/# python /src/bin/gatherer_standalone.py -c /conf/griffin-standalone.conf 
    08/12/2014 08:33:54 AM - griffinmcelroy.services.gatherer - INFO - loaded plugin demosnmp for type demosnmp
    08/12/2014 08:33:54 AM - griffinmcelroy.storage.webhdfs - INFO - mode: w filename: /tmp/webhdfs/samples
    08/12/2014 08:33:54 AM - webhdfs - DEBUG - Create directory: /webhdfs/v1/griffinmcelroy?op=MKDIRS&user.name=root
    08/12/2014 08:33:54 AM - webhdfs - DEBUG - HTTP Response: 200, OK
    08/12/2014 08:33:54 AM - griffinmcelroy.services.gatherer.standalone - INFO - starting poll
    08/12/2014 08:33:54 AM - griffinmcelroy.services.gatherer - INFO - got 1 samples from demosnmp
    08/12/2014 08:33:54 AM - griffinmcelroy.storage.webhdfs - DEBUG - did format
    08/12/2014 08:33:54 AM - griffinmcelroy.storage.webhdfs - DEBUG - did format
    08/12/2014 08:33:54 AM - griffinmcelroy.services.gatherer.standalone - INFO - persisted 1 samples

TODO - add docker config and containers for 0mq broker versions
