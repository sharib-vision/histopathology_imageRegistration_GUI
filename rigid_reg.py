#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 13:45:57 2019

@author: shariba
"""

'''
simpleITK image registration module test

'''

import SimpleITK as sitk

import sys
import os

useDebug = 0

def command_iteration(method) :
    print("{0:3} = {1:10.5f} : {2}".format(method.GetOptimizerIteration(),
                                   method.GetMetricValue(),
                                   method.GetOptimizerPosition()))

class HistopathologyRegistration():

    def rigid_registration(sourceImage, targetImage, transformationFILE):

        target_image = sitk.ReadImage(targetImage, sitk.sitkFloat32)
        source_image = sitk.ReadImage(sourceImage, sitk.sitkFloat32)

        R = sitk.ImageRegistrationMethod()
        R.SetMetricAsMeanSquares()
        R.SetOptimizerAsRegularStepGradientDescent(4.0, .01, 200 )
        R.SetInitialTransform(sitk.TranslationTransform(target_image.GetDimension()))
        R.SetInterpolator(sitk.sitkLinear)
        R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )

        outTx = R.Execute(target_image, source_image)

        print("-------")
        print(outTx)
        print("Optimizer stop condition: {0}".format(R.GetOptimizerStopConditionDescription()))
        print(" Iteration: {0}".format(R.GetOptimizerIteration()))
        print(" Metric value: {0}".format(R.GetMetricValue()))

        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(target_image);
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetDefaultPixelValue(100)
        resampler.SetTransform(outTx)

        out = resampler.Execute(source_image)
        sitk.WriteTransform(outTx,  transformationFILE)

        # set the Writer for imagewriter = sitk.ImageFileWriter()
        writer= sitk.ImageFileWriter()
        writer.SetFileName(transformationFILE.split('.')[0]+'_registered.tif')
        writer.Execute(out);
        print('pixelType of output: ', out.GetDepth())

        if useDebug:
            if ( not "SITK_NOSHOW" in os.environ ):
                simg1 = sitk.Cast(sitk.RescaleIntensity(target_image), sitk.sitkUInt8)
                simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
                cimg = sitk.Compose(simg1, simg2, simg1//2.-simg2//2.)
                sitk.Show( cimg, "ImageRegistration1 Composition" )

        return outTx


    def rigid_registration_MI(sourceImage, targetImage, transformationFILE):

        target_image = sitk.ReadImage(targetImage, sitk.sitkFloat32)
        source_image = sitk.ReadImage(sourceImage, sitk.sitkFloat32)

        numberOfBins = 24
        samplingPercentage = 0.10

        R = sitk.ImageRegistrationMethod()
        R.SetMetricAsMattesMutualInformation(numberOfBins)
        R.SetMetricSamplingPercentage(samplingPercentage,sitk.sitkWallClock)
        R.SetMetricSamplingStrategy(R.RANDOM)
        R.SetOptimizerAsRegularStepGradientDescent(1.0,.001,200)
        R.SetInitialTransform(sitk.TranslationTransform(target_image.GetDimension()))
        R.SetInterpolator(sitk.sitkLinear)

        R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )

        outTx = R.Execute(target_image, source_image)

        print("-------")
        print(outTx)
        print("Optimizer stop condition: {0}".format(R.GetOptimizerStopConditionDescription()))
        print(" Iteration: {0}".format(R.GetOptimizerIteration()))
        print(" Metric value: {0}".format(R.GetMetricValue()))

        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(target_image);
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetDefaultPixelValue(100)
        resampler.SetTransform(outTx)

        out = resampler.Execute(source_image)
        sitk.WriteTransform(outTx,  transformationFILE)

        # set the Writer for imagewriter = sitk.ImageFileWriter()
        writer= sitk.ImageFileWriter()
        writer.SetFileName(transformationFILE.split('.')[0]+'_MI.tif')
        writer.Execute(out);
        print('pixelType of output: ', out.GetDepth())

        if useDebug:
            if ( not "SITK_NOSHOW" in os.environ ):
                simg1 = sitk.Cast(sitk.RescaleIntensity(target_image), sitk.sitkUInt8)
                simg2 = sitk.Cast(sitk.RescaleIntensity(out), sitk.sitkUInt8)
                cimg = sitk.Compose(simg1, simg2, simg1//2.-simg2//2.)
                sitk.Show( cimg, "ImageRegistration1 Composition" )

        return outTx
    
    def non_rigid (sourceImage, targetImage, transformationFILE):
        
        target_image = sitk.ReadImage(targetImage, sitk.sitkFloat32)
        source_image = sitk.ReadImage(sourceImage, sitk.sitkFloat32)
        
        transformDomainMeshSize=[8]*source_image.GetDimension()
        tx = sitk.BSplineTransformInitializer(target_image, transformDomainMeshSize )
        
        R = sitk.ImageRegistrationMethod()
        R.SetMetricAsCorrelation()
        R.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5,
                       numberOfIterations=100,
                       maximumNumberOfCorrections=5,
                       maximumNumberOfFunctionEvaluations=1000,
                       costFunctionConvergenceFactor=1e+7)
        R.SetInitialTransform(tx, True)
        R.SetInterpolator(sitk.sitkLinear)
        
        R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )
        
        outTx = R.Execute(target_image, source_image)
        print("-------")
        print(outTx)
        print("Optimizer stop condition: {0}".format(R.GetOptimizerStopConditionDescription()))
        print(" Iteration: {0}".format(R.GetOptimizerIteration()))
        print(" Metric value: {0}".format(R.GetMetricValue()))
        
        return outTx
