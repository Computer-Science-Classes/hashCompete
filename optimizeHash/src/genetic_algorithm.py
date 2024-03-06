# src/genetic_algorithm.py
import datetime
import os
import logging
import sys
from deap import base, creator, tools, algorithms
import numpy as np
import matplotlib.pyplot as plt
import pickle
from multiprocessing import Pool
from hash_word_set import HashWordSet

book_list = [
    "books/pride_and_prejudice.txt",
    #"books/sense_and_sensibility.txt"
    #"books/wuthering_heights.txt",
]

# Setup logging
# log_filename = f"logs/evaluation_log_{datetime.now.strftime('%Y%m%d_%H%M%S')}.log"
# logging.basicConfig(filename=log_filename, level=logging.INFO)

def evaluate(individual):
    vowel_multiplier, endings_multiplier, consonant_multiplier, frequency_multiplier = individual  # Unpack the individual's parameters 

    # logging.info(f"Evaluating with vowel_multiplier={vowel_multiplier}, endings_multiplier={endings_multiplier}")


    # Calculate the average efficiency factor across all books
    total_efficiency_factor = 0
    for book_file in book_list:
        hash_set = HashWordSet(vowel_multiplier=vowel_multiplier, endings_multiplier=endings_multiplier,
                           consonant_multiplier=consonant_multiplier, frequency_multiplier=frequency_multiplier)
        with open(book_file, 'r', encoding='utf-8') as file:
            for line in file:
                for word in line.split():
                    hash_set.add(word)
        ef = hash_set.efficiency_factor()
        total_efficiency_factor += ef['efficiencyFactor']

    average_efficiency_factor = total_efficiency_factor / len(book_list)
    return (average_efficiency_factor,)

# Setup DEAP
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # We want to minimize our objective
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

toolbox.register("attr_vowel_multiplier", np.random.uniform, 0.1, 100)  # range
toolbox.register("attr_endings_multiplier", np.random.uniform, 0.1, 100)  # range
toolbox.register("attr_consonant_multiplier", np.random.uniform, 0.1, 100)  # range
toolbox.register("attr_frequency_multiplier", np.random.uniform, 0.1, 100)  # range

toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_vowel_multiplier, toolbox.attr_endings_multiplier, toolbox.attr_consonant_multiplier, toolbox.attr_frequency_multiplier), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    checkpoint_path = "checkpoints/"
    logs_path = "logs/"
    os.makedirs(checkpoint_path, exist_ok=True)
    os.makedirs(logs_path, exist_ok=True)


    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    logbook = tools.Logbook()
    logbook.header = ['gen', 'min', 'avg', 'std', 'max']

    # Set up the population
    pop = toolbox.population(n=50)
    hof = tools.HallOfFame(1)

    # Set up the multiprocessing pool
    pool = Pool()
    toolbox.register("map", pool.map)


    # Load from a previous checkpoint, if any
    cp_filename = os.path.join(checkpoint_path, "latest_checkpoint.pkl")
    if os.path.isfile(cp_filename):
        with open(cp_filename, "rb") as cp_file:
            cp = pickle.load(cp_file)
            pop = cp["population"]
            generation = cp["generation"]
            hof = cp['hof']
            logbook = cp['logbook']

            if len(logbook) > 0:
                generation = logbook[-1]["gen"] + 1
    else:
        generation = 0
        logbook.clear()

    # Estimate convergence
    convergence_threshold = 0.01
    num_generations_convergence = 5
    previous_avg_fitness = None
    convergence_count = 0
    max_generations = 100

    # Main evolutionary loop
    for gen in range (generation, max_generations):
        print(f"Starting Generation {generation}")

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)

        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame and statistics
        hof.update(pop)
        record = stats.compile(pop)
        logbook.record(gen=generation, **record)
        print(logbook.stream)

        # Check convergence
        if gen > 0 and abs(record['avg'] - logbook.select('avg')[-2]) < convergence_threshold:
            convergence_count += 1
        else:
            convergence_count = 0

        if convergence_count >= num_generations_convergence:
            print("Convergence likely reached.")
            break
            
        print(f"Convergence estimation: {num_generations_convergence - convergence_count} generations remaning until likely convergence")


        # Selection, Crossover, and Mutation
        offspring = toolbox.select(pop, len(pop))
        offspring = algorithms.varAnd(offspring, toolbox, cxpb=0.5, mutpb=0.4)

        # Replace the old population by the offspring
        pop[:] = offspring

        # Log to a single file per generation
        log_filename = os.path.join(logs_path, f"evaluation_log_gen_{generation}.txt")
        with open(log_filename, 'w') as log_file:
            log_file.write(f"Generation {generation}\n")
            log_file.write(f"Min Fitness: {record['min']}\n")
            log_file.write(f"Avg Fitness: {record['avg']}\n")
            log_file.write(f"Std Dev Fitness: {record['std']}\n")
            log_file.write(f"Max Fitness: {record['max']}\n")
            log_file.write("Hall of Fame Individuals:\n")
            for individual in hof:
                log_file.write(f"{individual}, Fitness: {individual.fitness.values}\n")

        # Checkpointing
        cp = {"population": pop, "generation": generation, "hof": hof, "logbook": logbook}
        with open(cp_filename, "wb") as cp_file:
            pickle.dump(cp, cp_file)

        if len(logbook) > 0:
            gens = range(len(logbook))
            min_fitness = logbook.select("min")
            avg_fitness = logbook.select("avg")

        # Log Hall of Fame
        for individual in hof:
                print(f"Hall of Famer: {individual}, Fitness: {individual.fitness.values}")

        hof_filename = os.path.join(logs_path, f"hall_of_fame_{os.getpid()}.txt")
        with open(hof_filename, 'a') as hof_file:
            for individual in hof:
                hof_file.write(f"Multiplier: {individual}, Fitness: {individual.fitness.values}\n")

        # Data dump and plotting for the current generation
        generation_csv = os.path.join(checkpoint_path, f"gen_{generation}_fitness.csv")
        with open(generation_csv, "w") as f:
            f.write("Generation, Min Fitness, Avg Fitness, Std Dev Fitness, Max Fitness\n")
            for gen in gens:
                f.write(f"{gen},{logbook.select('min')[gen]},{logbook.select('avg')[gen]},{logbook.select('std')[gen]},{logbook.select('max')[gen]}\n")
        
        plt.figure(figsize=(10, 5))
        plt.plot(gens, min_fitness, label="Min Fitness")
        plt.plot(gens, avg_fitness, label="Avg Fitness")
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.legend()
        plt.title(f"Fitness Over Generations up to {generation}")
        plt.savefig(os.path.join(checkpoint_path, f"gen_{generation}_fitness.png"))
        plt.close()

        generation += 1

    # Close the pool to free resources
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()