#include <Python.h>
#include "lib/cz_update.h"
#include "lib/ipdb_lib.h"
#include "lib/patch.c"

static PyObject *
qqwry_meta_parse(PyObject *self, PyObject *args)
{
    const unsigned char *buffer;
    int length;
    if (!PyArg_ParseTuple(args, "t#", &buffer, &length))
        return NULL;

    const cz_update *ctx = parse_cz_update(buffer, length);
    if(!ctx) return NULL;

    return PyLong_FromLong(get_cz_update_date(ctx));
}

static PyObject *
qqwry_decode(PyObject *self, PyObject *args)
{
    const unsigned char *buffer;
    int length;

    unsigned char *qqwry_buffer;
    int qqwry_length;
    if (!PyArg_ParseTuple(args, "t#s#", &buffer, &length, &qqwry_buffer, &qqwry_length))
        return NULL;

    const cz_update *ctx = parse_cz_update(buffer, length);
    if(!ctx) return NULL;

    uint32_t output_len;
    uint8_t *output = decode_cz_update(ctx, qqwry_buffer, qqwry_length, &output_len);
    if(!output) return NULL;

    PyObject *ret = Py_BuildValue("s#", output, output_len);
    free(output);

    return ret;
}

static PyObject *
qqwry_make_patch(PyObject *self, PyObject *args)
{
    const unsigned char *buffer1, *buffer2;
    int length1, length2;
    if (!PyArg_ParseTuple(args, "t#t#", &buffer1, &length1, &buffer2, &length2))
        return NULL;

    ipdb *db1 = ipdb_create(&qqwry_handle, buffer1, length1, NULL);
    ipdb *db2 = ipdb_create(&qqwry_handle, buffer2, length2, NULL);

    if(db1 && db2)
    {
        make_patch(db1, db2);
    }

    if(db1) ipdb_release(db1);
    if(db2) ipdb_release(db2);

    return PyLong_FromLong(1);
}

static PyMethodDef QQWryMethods[] = {
    {"meta_parse",  qqwry_meta_parse, METH_VARARGS, "parse the meta file copywrite.rar"},
    {"decode",  qqwry_decode, METH_VARARGS, "decode the qqwry.rar to qqwry.dat"},
    {"make_patch",  qqwry_make_patch, METH_VARARGS, "make the patch from two qqwry.dat"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initqqwry(void)
{
    (void) Py_InitModule("qqwry", QQWryMethods);
}
