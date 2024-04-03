"""Unittest for meta-data consistency."""

# build-in modules
import os
import tempfile
import unittest

# third-party modules
import numpy

# own modules
from medpy.core.logger import Logger
from medpy.io import header, load, save

# path changes


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.2, 2013-05-24"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Meta-data consistency unittest."


# code
class TestMetadataConsistency(unittest.TestCase):
    ####
    # Comprehensive list of image format endings
    ####
    # The most important image formats for medical image processing
    __important = [
        ".nii",
        ".nii.gz",
        ".hdr",
        ".img",
        ".img.gz",
        ".dcm",
        ".dicom",
        ".mhd",
        ".nrrd",
        ".mha",
    ]

    # list of image formats ITK is theoretically able to load
    __itk = [
        ".analyze",  # failed saving
        ".hdr",
        ".img",
        ".bmp",
        ".dcm",
        ".gdcm",  # failed saving
        ".dicom",
        ".4x",  # failed saving
        ".5x",  # failed saving
        ".ge",  # failed saving
        ".ge4",  # failed saving
        ".ge4x",  # failed saving
        ".ge5",  # failed saving
        ".ge5x",  # failed saving
        ".gipl",
        ".h5",
        ".hdf5",
        ".he5",
        ".ipl",  # failed saving
        ".jpg",
        ".jpeg",
        ".lsm",
        ".mha",
        ".mhd",
        ".pic",
        ".png",
        ".raw",  # failed saving
        ".vision",  # failed saving
        ".siemens",  # failed saving
        ".spr",
        ".sdt",  # failed saving
        ".stimulate",  # failed saving
        ".tif",
        ".tiff",
        ".vtk",
        ".bio",  # failed saving
        ".biorad",  # failed saving
        ".brains",  # failed saving
        ".brains2",  # failed saving
        ".brains2mask",  # failed saving
        ".bruker",  # failed saving
        ".bruker2d",  # failed saving
        ".bruker2dseq",  # failed saving
        ".mnc",  # failed saving
        ".mnc2",  # failed saving
        ".minc",  # failed saving
        ".minc2",  # failed saving
        ".nii",
        ".nifti",  # failed saving
        ".nhdr",
        ".nrrd",
        ".philips",  # failed saving
        ".philipsreq",  # failed saving
        ".rec",  # failed saving
        ".par",  # failed saving
        ".recpar",  # failed saving
        ".vox",  # failed saving
        ".voxbo",  # failed saving
        ".voxbocub",  # failed saving
    ]

    ##########
    # Combinations to avoid due to technical problems, dim->file ending pairs
    ##########
    __avoid = {
        3: (
            ".mnc",
            ".mnc2",
        ),  # cause segmentation faults in simpleITK
        4: (
            ".mnc",
            ".mnc2",
        ),  # cause segmentation faults in simpleITK
        5: (
            ".mnc",
            ".mnc2",
        ),  # cause segmentation faults in simpleITK
    }  # e.g. {4: ('.dcm', '.dicom')}

    ##########
    # Error delta: the maximum difference between to meta-data entries that is still considered consistent (required, as there may be rounding errors)
    ##########
    __delta = 0.0001

    def test_MetadataConsistency(self):
        """
        This test checks the ability of different image formats to consistently save
        meta-data information. Especially if a conversion between formats is required,
        that involves different 3rd party modules, this is not always guaranteed.

        The images are saved in one format, loaded and then saved in another format.
        Subsequently the differences in the meta-data is checked.

        Currently this test can only check:
        - voxel spacing
        - image offset

        Note that some other test are inherently performed by the
        loadsave.TestIOFacilities class:
        - data type
        - shape
        - content

        With the verboose switches, a comprehensive list of the results can be obtianed.
        """
        ####
        # VERBOOSE SETTINGS
        # The following are two variables that can be used to print some nicely
        # formatted additional output. When one of them is set to True, this unittest
        # should be run stand-alone.
        ####
        # Print a list of format to format conversion which preserve meta-data
        consistent = True
        # Print a list of format to format conversion which do not preserve meta-data
        inconsistent = False
        # Print a list of formats that failed conversion in general
        unsupported = False

        ####
        # OTHER SETTINGS
        ####
        # debug settings
        logger = Logger.getInstance()
        # logger.setLevel(logging.DEBUG)

        # run test either for most important formats or for all (see loadsave.TestIOFacilities)
        # __suffixes = self.__important # (choice 1)
        __suffixes = self.__important + self.__itk  # (choice 2)

        # dimensions and dtypes to check
        __suffixes = list(set(__suffixes))
        __ndims = [1, 2, 3, 4, 5]
        __dtypes = [
            numpy.bool_,
            numpy.int8,
            numpy.int16,
            numpy.int32,
            numpy.int64,
            numpy.uint8,
            numpy.uint16,
            numpy.uint32,
            numpy.uint64,
            numpy.float32,
            numpy.float64,  # numpy.float128, # last one removed, as not present on every machine
            numpy.complex64,
            numpy.complex128,
        ]  # numpy.complex256 ## removed, as not present on every machine

        # prepare struct to save settings that passed the test
        consistent_types = dict.fromkeys(__suffixes)
        for k0 in consistent_types:
            consistent_types[k0] = dict.fromkeys(__suffixes)
            for k1 in consistent_types[k0]:
                consistent_types[k0][k1] = dict.fromkeys(__ndims)
                for k2 in consistent_types[k0][k1]:
                    consistent_types[k0][k1][k2] = []

        # prepare struct to save settings that did not
        inconsistent_types = dict.fromkeys(__suffixes)
        for k0 in inconsistent_types:
            inconsistent_types[k0] = dict.fromkeys(__suffixes)
            for k1 in inconsistent_types[k0]:
                inconsistent_types[k0][k1] = dict.fromkeys(__ndims)
                for k2 in inconsistent_types[k0][k1]:
                    inconsistent_types[k0][k1][k2] = dict.fromkeys(__dtypes)

        # prepare struct to save settings that did not pass the data integrity test
        unsupported_types = dict.fromkeys(__suffixes)
        for k0 in consistent_types:
            unsupported_types[k0] = dict.fromkeys(__suffixes)
            for k1 in unsupported_types[k0]:
                unsupported_types[k0][k1] = dict.fromkeys(__ndims)
                for k2 in unsupported_types[k0][k1]:
                    unsupported_types[k0][k1][k2] = dict.fromkeys(__dtypes)

        # create artifical images, save them, load them again and compare them
        path = tempfile.mkdtemp()
        try:
            for ndim in __ndims:
                logger.debug("Testing for dimension {}...".format(ndim))
                arr_base = numpy.random.randint(0, 10, list(range(10, ndim + 10)))
                for dtype in __dtypes:
                    arr_save = arr_base.astype(dtype)
                    for suffix_from in __suffixes:
                        # do not run test, if in avoid array
                        if ndim in self.__avoid and suffix_from in self.__avoid[ndim]:
                            unsupported_types[suffix_from][suffix_from][ndim][
                                dtype
                            ] = "Test skipped, as combination in the tests __avoid array."
                            continue

                        # save array as file, load again to obtain header and set the meta-data
                        image_from = "{}/img{}".format(path, suffix_from)
                        try:
                            save(arr_save, image_from, None, True)
                            if not os.path.exists(image_from):
                                raise Exception(
                                    "Image of type {} with shape={}/dtype={} has been saved without exception, but the file does not exist.".format(
                                        suffix_from, arr_save.shape, dtype
                                    )
                                )
                        except Exception as e:
                            unsupported_types[suffix_from][suffix_from][ndim][dtype] = (
                                e.message if hasattr(e, "message") else str(e.args)
                            )
                            continue

                        try:
                            img_from, hdr_from = load(image_from)
                            img_from = img_from.astype(
                                dtype
                            )  # change dtype of loaded image again, as sometimes the type is higher (e.g. int64 instead of int32) after loading!
                        except Exception as e:
                            _message = (
                                e.message if hasattr(e, "message") else str(e.args)
                            )
                            unsupported_types[suffix_from][suffix_from][ndim][
                                dtype
                            ] = "Saved reference image of type {} with shape={}/dtype={} could not be loaded. Reason: {}".format(
                                suffix_from, arr_save.shape, dtype, _message
                            )
                            continue

                        header.set_voxel_spacing(
                            hdr_from,
                            [
                                numpy.random.rand() * numpy.random.randint(1, 10)
                                for _ in range(img_from.ndim)
                            ],
                        )
                        try:
                            header.set_voxel_spacing(
                                hdr_from,
                                [
                                    numpy.random.rand() * numpy.random.randint(1, 10)
                                    for _ in range(img_from.ndim)
                                ],
                            )
                            header.set_offset(
                                hdr_from,
                                [
                                    numpy.random.rand() * numpy.random.randint(1, 10)
                                    for _ in range(img_from.ndim)
                                ],
                            )
                        except Exception as e:
                            logger.error(
                                "Could not set the header meta-data for image of type {} with shape={}/dtype={}. This should not happen and hints to a bug in the code. Signaled reason is: {}".format(
                                    suffix_from, arr_save.shape, dtype, e
                                )
                            )
                            unsupported_types[suffix_from][suffix_from][ndim][dtype] = (
                                e.message if hasattr(e, "message") else str(e.args)
                            )
                            continue

                        for suffix_to in __suffixes:
                            # do not run test, if in avoid array
                            if ndim in self.__avoid and suffix_to in self.__avoid[ndim]:
                                unsupported_types[suffix_from][suffix_to][ndim][
                                    dtype
                                ] = "Test skipped, as combination in the tests __avoid array."
                                continue

                            # for each other format, try format to format conversion an check if the meta-data is consistent
                            image_to = "{}/img_to{}".format(path, suffix_to)
                            try:
                                save(img_from, image_to, hdr_from, True)
                                if not os.path.exists(image_to):
                                    raise Exception(
                                        "Image of type {} with shape={}/dtype={} has been saved without exception, but the file does not exist.".format(
                                            suffix_to, arr_save.shape, dtype
                                        )
                                    )
                            except Exception as e:
                                unsupported_types[suffix_from][suffix_from][ndim][
                                    dtype
                                ] = (
                                    e.message if hasattr(e, "message") else str(e.args)
                                )
                                continue

                            try:
                                _, hdr_to = load(image_to)
                            except Exception as e:
                                _message = (
                                    e.message if hasattr(e, "message") else str(e.args)
                                )
                                unsupported_types[suffix_from][suffix_to][ndim][
                                    dtype
                                ] = "Saved testing image of type {} with shape={}/dtype={} could not be loaded. Reason: {}".format(
                                    suffix_to, arr_save.shape, dtype, _message
                                )
                                continue

                            msg = self.__diff(hdr_from, hdr_to)
                            if msg:
                                inconsistent_types[suffix_from][suffix_to][ndim][
                                    dtype
                                ] = msg
                            else:
                                consistent_types[suffix_from][suffix_to][ndim].append(
                                    dtype
                                )

                            # remove testing image
                            if os.path.exists(image_to):
                                os.remove(image_to)

                        # remove reference image
                        if os.path.exists(image_to):
                            os.remove(image_to)

        except Exception:
            if not os.listdir(path):
                os.rmdir(path)
            else:
                logger.debug(
                    "Could not delete temporary directory {}. Is not empty.".format(
                        path
                    )
                )
            raise

        if consistent:
            print("\nthe following format conversions are meta-data consistent:")
            print("from\tto\tndim\tdtypes")
            for suffix_from in consistent_types:
                for suffix_to in consistent_types[suffix_from]:
                    for ndim, dtypes in list(
                        consistent_types[suffix_from][suffix_to].items()
                    ):
                        if list == type(dtypes) and not 0 == len(dtypes):
                            print(
                                (
                                    "{}\t{}\t{}D\t{}".format(
                                        suffix_from,
                                        suffix_to,
                                        ndim,
                                        [str(x).split(".")[-1][:-2] for x in dtypes],
                                    )
                                )
                            )
        if inconsistent:
            print("\nthe following form conversions are not meta-data consistent:")
            print("from\tto\tndim\tdtype\t\terror")
            for suffix_from in inconsistent_types:
                for suffix_to in inconsistent_types[suffix_from]:
                    for ndim in inconsistent_types[suffix_from][suffix_to]:
                        for dtype, msg in list(
                            inconsistent_types[suffix_from][suffix_to][ndim].items()
                        ):
                            if msg:
                                print(
                                    (
                                        "{}\t{}\t{}D\t{}\t\t{}".format(
                                            suffix_from,
                                            suffix_to,
                                            ndim,
                                            str(dtype).split(".")[-1][:-2],
                                            msg,
                                        )
                                    )
                                )

        if unsupported:
            print("\nthe following form conversions could not be tested due to errors:")
            print("from\tto\tndim\tdtype\t\terror")
            for suffix_from in unsupported_types:
                for suffix_to in unsupported_types[suffix_from]:
                    for ndim in unsupported_types[suffix_from][suffix_to]:
                        for dtype, msg in list(
                            unsupported_types[suffix_from][suffix_to][ndim].items()
                        ):
                            if msg:
                                print(
                                    (
                                        "{}\t{}\t{}D\t{}\t\t{}".format(
                                            suffix_from,
                                            suffix_to,
                                            ndim,
                                            str(dtype).split(".")[-1][:-2],
                                            msg,
                                        )
                                    )
                                )

    def __diff(self, hdr1, hdr2):
        """
        Returns an error message if the meta-data of the supplied headers differ,
        otherwise False.
        """
        if not self.__same_seq(
            header.get_voxel_spacing(hdr1), header.get_voxel_spacing(hdr2)
        ):
            return "the voxel spacing is not consistent: {} != {}".format(
                header.get_voxel_spacing(hdr1), header.get_voxel_spacing(hdr2)
            )
        if not self.__same_seq(header.get_offset(hdr1), header.get_offset(hdr2)):
            return "the offset is not consistent: {} != {}".format(
                header.get_offset(hdr1), header.get_offset(hdr2)
            )
            # return 'the offset is not consistent: {} != {}\n{} / {}\n{} / {}'.format(header.get_offset(hdr1), header.get_offset(hdr2), type(hdr1), type(hdr2), hdr2.NumberOfFrames if "NumberOfFrames" in hdr2 else "NONE", hdr2.ImagePositionPatient if "ImagePositionPatient" in hdr2 else 'NONE')
        else:
            return False

    def __same_seq(self, seq1, seq2):
        if len(seq1) != len(seq2):
            return False
        for e1, e2 in zip(seq1, seq2):
            diff = abs(e1 - e2)
            if diff > self.__delta:
                return False
        return True


if __name__ == "__main__":
    unittest.main()
