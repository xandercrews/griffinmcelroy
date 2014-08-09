__author__ = 'achmed'

import collections
from pyVmomi import vmodl, vim


def build_full_traversal():
    '''
    Builds a traversal spec that will recurse through all objects .. or at least
    I think it does. additions welcome.

    See com.vmware.apputils.vim25.ServiceUtil.build_full_traversal in the java API.
    Extended by Sebastian Tello's examples from pysphere to reach networks and datastores.
    '''
    TraversalSpec = vmodl.query.PropertyCollector.TraversalSpec
    SelectionSpec = vmodl.query.PropertyCollector.SelectionSpec

    # Recurse through all resourcepools
    rpToRp = TraversalSpec(name='rpToRp', type=vim.ResourcePool, path="resourcePool", skip=False)

    rpToRp.selectSet.extend(
        (
            SelectionSpec(name="rpToRp"),
            SelectionSpec(name="rpToVm"),
        )
    )

    rpToVm = TraversalSpec(name='rpToVm', type=vim.ResourcePool, path="vm", skip=False)

    # Traversal through resourcepool branch
    crToRp = TraversalSpec(name='crToRp', type=vim.ComputeResource, path='resourcePool', skip=False)
    crToRp.selectSet.extend(
        (
            SelectionSpec(name='rpToRp'),
            SelectionSpec(name='rpToVm'),
        )
    )

    # Traversal through host branch
    crToH = TraversalSpec(name='crToH', type=vim.ComputeResource, path='host', skip=False)

    # Traversal through hostFolder branch
    dcToHf = TraversalSpec(name='dcToHf', type=vim.Datacenter, path='hostFolder', skip=False)
    dcToHf.selectSet.extend(
        (
            SelectionSpec(name='visitFolders'),
        )
    )

    # Traversal through vmFolder branch
    dcToVmf = TraversalSpec(name='dcToVmf', type=vim.Datacenter, path='vmFolder', skip=False)
    dcToVmf.selectSet.extend(
        (
            SelectionSpec(name='visitFolders'),
        )
    )

    # Traversal through network folder branch
    dcToNet = TraversalSpec(name='dcToNet', type=vim.Datacenter, path='networkFolder', skip=False)
    dcToNet.selectSet.extend(
        (
            SelectionSpec(name='visitFolders'),
        )
    )

    # Traversal through datastore branch
    dcToDs = TraversalSpec(name='dcToDs', type=vim.Datacenter, path='datastore', skip=False)
    dcToDs.selectSet.extend(
        (
            SelectionSpec(name='visitFolders'),
        )
    )

    # Recurse through all hosts
    hToVm = TraversalSpec(name='hToVm', type=vim.HostSystem, path='vm', skip=False)
    hToVm.selectSet.extend(
        (
            SelectionSpec(name='visitFolders'),
        )
    )

    # Recurse through the folders
    visitFolders = TraversalSpec(name='visitFolders', type=vim.Folder, path='childEntity',
                                 skip=False)
    visitFolders.selectSet.extend(
        (
            SelectionSpec(name='visitFolders'),
            SelectionSpec(name='dcToHf'),
            SelectionSpec(name='dcToVmf'),
            SelectionSpec(name='dcToNet'),
            SelectionSpec(name='crToH'),
            SelectionSpec(name='crToRp'),
            SelectionSpec(name='dcToDs'),
            SelectionSpec(name='hToVm'),
            SelectionSpec(name='rpToVm'),
        )
    )

    fullTraversal = SelectionSpec.Array(
        (visitFolders, dcToHf, dcToVmf, dcToNet, crToH, crToRp, dcToDs, rpToRp, hToVm, rpToVm,))

    return fullTraversal


def make_full_property_set(motypes):
    propSet = []

    for motype in motypes:
        propSpec = vmodl.query.PropertyCollector.PropertySpec(type=motype, all=True)
        propSet.append(propSpec)

    return propSet


def make_property_sets_from_propspec(propspec):
    assert isinstance(propspec, collections.Mapping)

    propSet = []

    props = map(_translate_motypes, propspec.items())

    for motype, proplist in props:
        if len(proplist) == 0:
            continue
        propSpec = vmodl.query.PropertyCollector.PropertySpec(type=motype, all=False)
        propSpec.pathSet.extend(proplist)
        propSet.append(propSpec)

    return propSet


def _translate_motypes(proptuple):
    assert len(proptuple) == 2

    if isinstance(proptuple[0], (basestring, unicode)):
        motype, proplist = proptuple
        motype = getattr(vim, motype, None)
        assert motype is not None, 'motype must be valid'
        return (motype, proplist,)
    else:
        return proptuple


def make_full_object_specs(vc):
    objSpec = vmodl.query.PropertyCollector.ObjectSpec(obj=vc.content.rootFolder,
                                                       selectSet=build_full_traversal())
    objSpecs = [objSpec]

    return objSpecs

def get_object_properties_by_propspec(vc, propspec):
    content = vc.RetrieveContent()

    fspec = vim.PropertyCollector.FilterSpec(objectSet=make_full_object_specs(vc), propSet=make_property_sets_from_propspec(propspec), reportMissingObjectsInResults=False)
    retopts = vim.PropertyCollector.RetrieveOptions()

    objects = []

    responseprops = content.propertyCollector.RetrievePropertiesEx(specSet=[fspec], options=retopts)
    objects += responseprops.objects
    while responseprops.token:
        responseprops = content.propertyCollector.ContinueRetrievePropertiesEx(token=responseprops.token)
        objects += responseprops.objects

    return objects
