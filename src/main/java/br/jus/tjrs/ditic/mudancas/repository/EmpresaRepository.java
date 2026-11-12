package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.Empresa;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface EmpresaRepository extends JpaRepository<Empresa, Long> {

    Optional<Empresa> findByNome(String nome);

    List<Empresa> findAllByOrderByNomeAsc();
}
