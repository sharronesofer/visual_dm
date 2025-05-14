from typing import Dict, List, Optional, Any, Union

/**
 * Implementation of a generation pipeline that processes input through a series of steps
 */
class GenerationPipeline<TInput, TOutput> implements IGenerationPipeline<TInput, TOutput> {
    private steps: IPipelineStep<any, any>[] = [];
    /**
     * Create a new generation pipeline
     * @param steps Optional initial steps to add to the pipeline
     */
    constructor(steps: IPipelineStep<any, any>[] = []) {
        this.steps = [...steps];
    }
    /**
     * Add a new step to the pipeline
     * @param step The pipeline step to add
     * @returns This pipeline instance (for chaining)
     */
    public addStep<TIntermediate>(step: IPipelineStep<TInput, TIntermediate>): IGenerationPipeline<TIntermediate, TOutput> {
        this.steps.push(step);
        return this as unknown as IGenerationPipeline<TIntermediate, TOutput>;
    }
    /**
     * Execute the pipeline with the given input
     * @param input The input to the first step
     * @param random The random number generator to use
     * @returns The output of the last step
     */
    public execute(input: TInput, random: IRandomGenerator): TOutput {
        if (this.steps.length === 0) {
            throw new Error('Cannot execute an empty pipeline');
        }
        let result: any = input;
        for (const step of this.steps) {
            result = step.process(result, random);
        }
        return result as TOutput;
    }
    /**
     * Get the number of steps in the pipeline
     * @returns The number of steps
     */
    public stepCount(): number {
        return this.steps.length;
    }
    /**
     * Create a pipeline step from a function
     * @param processFn The function to use for processing
     * @returns A pipeline step
     */
    public static createStep<TIn, TOut>(
        processFn: (input: TIn, random: IRandomGenerator) => TOut
    ): IPipelineStep<TIn, TOut> {
        return {
            process: processFn
        };
    }
} 